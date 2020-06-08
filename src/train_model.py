import sys
import pathlib
import pandas as pd
import numpy as np
import math
import scipy
import xgboost as xgb
import pickle as pkl
import logging
import logging.config
import yaml

# Modeling packages
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import VotingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error

# User-written modules
import config
from src.helpers import upload_to_s3, check_for_valid_cols

logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def run_train_model(args):
    """Perform model training (imputation, hyperparameter search) and obtain trained model object

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - input: local file path of features data file
            - output: local file path to output the features data
            - use_existing_params: specification of whether to use existing hyperparameter configs
            - upload: specification of whether to upload model artifacts to S3
            - s3_bucket_name: name of S3 bucket to upload model artifacts to
    """

    logger.info("Reading in configs from modelconfig.yml.")
    try:
        # Load in configs from yml file
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            s3_objects = config["s3_objects"]
            data_files = config["data_files"]
            model_files = config["model_files"]

            # Feature lists and dictionaries for transformations
            HOST_RESPONSE_MAP = config["train_model"]["HOST_RESPONSE_MAP"]
            TARGET_COL = config["TARGET_COL"]
            IMPUTE_COLS = config["train_model"]["IMPUTE_COLS"]
            COLS_NUM_STD = config["train_model"]["COLS_NUM_STD"]
            COLS_NUM_MINMAX = config["train_model"]["COLS_NUM_MINMAX"]
            COLS_CAT = config["train_model"]["COLS_CAT"]

            # Model object settings
            iter_imp_settings = config["train_model"]["iter_imp_settings"]
            train_test_settings = config["train_model"]["train_test_settings"]
            tuning_param_settings = config["train_model"]["tuning_param_settings"]
            grid_search_settings = config["train_model"]["grid_search_settings"]
            voting_model_settings = config["train_model"]["voting_model_settings"]
            tuned_params = config["train_model"]["tuned_params"]
    except KeyError:
        logger.error(
            "Encountered error when assigning variable from configurations file."
        )
        sys.exit(1)
    except (FileNotFoundError, IOError):
        logger.error("Encountered error in reading in the configurations file.")
        sys.exit(1)

    # Read in features dataset
    if args.input is None:
        logger.info(
            "Reading in features data file {}.".format(
                data_files["DATA_FILENAME_FEATURES"]
            )
        )
        df = pd.read_csv(data_files["DATA_FILENAME_FEATURES"])
    else:
        logger.info("Reading in features data file {}.".format(args.input))
        df = pd.read_csv(args.input)

    # Check that all features expected are in the dataframe
    logger.debug("Checking that expected feature are in the dataframe.")
    IMPUTE_COLS = check_for_valid_cols(IMPUTE_COLS, df)
    COLS_NUM_STD = check_for_valid_cols(COLS_NUM_STD, df)
    COLS_NUM_MINMAX = check_for_valid_cols(COLS_NUM_MINMAX, df)
    COLS_CAT = check_for_valid_cols(COLS_CAT, df)

    # Impute missing values
    dummy_cols = [col for col in COLS_CAT if col not in IMPUTE_COLS]
    logger.debug("Imputing features {}.".format(IMPUTE_COLS))
    df_imputed = get_imputed_values(
        df[df.columns[~df.columns.isin([TARGET_COL])]],
        dummy_cols,
        iter_imp_settings,
        HOST_RESPONSE_MAP,
    )
    df.loc[:, IMPUTE_COLS] = df_imputed[IMPUTE_COLS]

    # One hot encode all categorical variables to get final dataframe for model development
    logger.debug("Encoding categorical features {}.".format(COLS_CAT))
    df_model, enc = encode_variables(df, COLS_CAT)

    # Develop trained model object
    logger.info("Training model and obtaining model artifacts.")
    tmo, stdscaler, minmaxscaler = get_trained_model_object(
        df_model,
        TARGET_COL,
        train_test_settings,
        COLS_NUM_STD,
        COLS_NUM_MINMAX,
        tuning_param_settings,
        grid_search_settings,
        voting_model_settings,
        tuned_params=tuned_params,
        use_existing_params=args.use_existing_params,
    )
    logger.info("Obtained trained model object and model artifacts.")

    # Output model and encoder to pkl file
    if args.output is None:
        model_file_tmo = model_files["MODEL_FILENAME_TMO"]
        model_file_encoder = model_files["MODEL_FILENAME_ENCODER"]
        model_file_scalers = model_files["MODEL_FILENAME_SCALERS"]
    else:
        model_file_tmo = pathlib.Path(args.output) / "model.pkl"
        model_file_encoder = pathlib.Path(args.output) / "encoders.pkl"
        model_file_scalers = pathlib.Path(args.output) / "scalers.pkl"

    with open(model_file_tmo, "wb") as file:
        logger.info("Writing trained model object to {}.".format(model_file_tmo))
        pkl.dump(tmo, file)
    with open(model_file_encoder, "wb") as file:
        logger.info("Writing encoder object to {}.".format(model_file_encoder))
        pkl.dump(enc, file)
    with open(model_file_scalers, "wb") as file:
        logger.info("Writing scaler objects to {}.".format(model_file_scalers))
        pkl.dump((stdscaler, minmaxscaler), file)

    # Upload to S3 if chosen
    if args.upload:
        logger.info(
            "Uploading model artifacts to S3 bucket {}.".format(args.s3_bucket_name)
        )
        upload_to_s3(
            model_files["MODEL_FILENAME_TMO"],
            args.s3_bucket_name,
            s3_objects["S3_OBJECT_MODEL_TMO"],
        )
        logger.info(
            "Uploading {} to S3 bucket {}.".format(
                model_files["MODEL_FILENAME_ENCODER"], args.s3_bucket_name
            )
        )
        upload_to_s3(
            model_files["MODEL_FILENAME_ENCODER"],
            args.s3_bucket_name,
            s3_objects["S3_OBJECT_MODEL_ENCODER"],
        )
        logger.info(
            "Uploading {} to S3 bucket {}.".format(
                model_files["MODEL_FILENAME_SCALERS"], args.s3_bucket_name
            )
        )
        upload_to_s3(
            model_files["MODEL_FILENAME_SCALERS"],
            args.s3_bucket_name,
            s3_objects["S3_OBJECT_MODEL_SCALERS"],
        )


def get_imputed_values(df, dummy_cols, settings, host_response_map):
    """Imputes missing values for features with known missing values.

    Args:
        df (:class:`pandas.DataFrame`): listings data
        dummy_cols (:obj:`list`): columns to convert to dummy variables prior to imputation
        settings (:obj:`dict`): settings for the IterativeImputer
        host_response_map (:obj:`dict`): mapping of host_response_time categories to numerical values

    Returns:
        :class:`pandas.DataFrame`: listings data with imputed values
    """

    # One hot encode nominal categorical variables for iterative imputer
    logger.debug("Getting dummy variables for columns {}.".format(dummy_cols))
    df = pd.get_dummies(df, columns=dummy_cols, drop_first=True)

    # Use median for security_deposit and cleaning_fee
    num_values = dict()
    if "cleaning_fee" in df.columns.tolist():
        num_values.update({"cleaning_fee": df["cleaning_fee"].median()})
        logger.debug("Filling in NAs for cleaning_fee with median.")
        df = df.fillna(value=num_values)
    if "security_deposit" in df.columns.tolist():
        num_values.update({"security_deposit": df["security_deposit"].median()})
        logger.debug("Filling in NAs for security_deposit with median.")
        df = df.fillna(value=num_values)

    # Map host_response_time to numerical values and drop original column
    if "host_response_time" in df.columns.tolist():
        logger.debug("Mapping host_response_time to numerical values.")
        df.loc[:, "host_response_time_code"] = df["host_response_time"].map(
            host_response_map
        )
        df = df.drop(columns="host_response_time")

    # Set imputer settings to impute host_response_rate and host_response_time_code
    logger.debug("Setting iterative imputer with settings {}.".format(settings))
    imp = IterativeImputer(**settings)

    # Get column names
    colnames = df.columns.tolist()

    # Final imputed dataframe, excluding response variable)
    try:
        df_imp = pd.DataFrame(imp.fit_transform(df), columns=colnames)

        # Round the imputed values
        if "host_response_rate" in df.columns.tolist():
            logger.debug("Rounding imputed host_response_rate.")
            df_imp.loc[:, "host_response_rate"] = round(
                np.minimum(df_imp["host_response_rate"], 1.0), 2
            )
        if "host_response_time_code" in df.columns.tolist():
            logger.debug("Rounding host_response_time_code to integer values.")
            df_imp.loc[:, "host_response_time_code"] = round(
                df_imp["host_response_time_code"], 0
            ).astype(int)
            # Invert the host response time map
            inv_map = {v: k for k, v in host_response_map.items()}
            logger.debug(
                "Re-mapping integer values for host_response_time to categorical values."
            )
            df_imp.loc[:, "host_response_time"] = df_imp["host_response_time_code"].map(
                inv_map
            )

        return df_imp

    except Exception as e:
        logger.error("Encountered error when applying Iterative Imputer.")
        logger.error(e)
        return None


def encode_variables(df, cols):
    """One hot encode categorical variables

    Args:
        df (:class:`pandas.DataFrame`): listings data
        cols (:obj:`list`): list of categorical variables to one-hot encode

    Returns:
        :class:`pandas.DataFrame`: listings data with one-hot encoded categorical features
        :class:`sklearn.preprocessing.OneHotEncoder`: encoder object
    """

    # Define encoder
    enc = OneHotEncoder(drop="first")

    try:
        # Fit encoder to categorical columns
        enc.fit(df[cols])

        # Transform categorical predictors
        df_enc = pd.DataFrame(
            enc.transform(df[cols]).toarray(), columns=enc.get_feature_names(cols)
        )

        # Merge one-hot encoded columns with dataframe and drop original features
        df = df.join(df_enc).drop(columns=cols)

        return df, enc

    except Exception as e:
        logger.error("Encountered error while one-hot encoding categorical variables.")
        logger.error(e)
        sys.exit(1)


def get_trained_model_object(
    df,
    target_col,
    train_test_settings,
    cols_num_std=None,
    cols_num_minmax=None,
    tuning_param_settings=None,
    grid_search_settings=None,
    voting_model_settings=None,
    tuned_params=None,
    use_existing_params=False,
):
    """Performs input data transformations, hyperparameter tuning (if specified), and model fitting to
    obtain trained model object and model artifacts.

    Args:
        df (:class:`pandas.DataFrame`): entire input data for developing model
        target_col (str): target variable
        train_test_settings (:obj:`dict`): settings for splitting the train vs. test set
        cols_num_std (:obj:`list`, optional): list of columns to apply normalized standardization. Defaults to None.
        cols_num_minmax (:obj:`list`, optional): list of columns to apply minmax standardization. Defaults to None.
        tuning_param_settings (:obj:`dict`, optional): settings for tuning all model hyperparameters via random grid search. Defaults to None.
        grid_search_settings (:obj:`dict`, optional): settings for random grid search. Defaults to None.
        voting_model_settings (:obj:`dict`, optional): settings for voting ensemble model. Defaults to None.
        tuned_params (:obj:`dict`, optional): previously tuned parameters for all models. Defaults to None.
        use_existing_params (bool, optional): specification of whether to use `tuned_params`. Defaults to False.

    Returns:
        :class:`sklearn.ensemble.VotingRegressor`: trained model object
        :class:`sklearn.preprocessing.StandardScaler`: standard scaler object
        :class:`sklearn.preprocessing.MinMaxScaler`: minmax scaler object
    """

    # List to contain all models fitted
    models_all = []

    # Split into train / test set and log transform target variable
    X = df[[col for col in df.columns if col != target_col]]
    logger.debug("Taking log transform of target variabble.")
    y = np.log(df[target_col])

    logger.info("Splitting dataset into train and test set")
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, **train_test_settings)
        logger.info(
            "Train data shape: {} rows, {} columns.".format(
                X_train.shape[0], X_train.shape[1]
            )
        )
        logger.info(
            "Test data shape: {} rows, {} columns.".format(
                X_test.shape[0], X_test.shape[1]
            )
        )
        logger.warning(
            "Total of {} rows between train and test set. Expected {}.".format(
                X_train.shape[0] + X_test.shape[0], df.shape[0]
            )
        )
    except Exception as e:
        logger.error("Encountered error when splitting data into train and test set.")
        logger.error(e)
        sys.exit(1)

    # Standardize predictors by defining scalers
    logger.info("Standardizing features.")
    stdscaler = StandardScaler()
    stdscaler.fit(X_train[cols_num_std])
    minmaxscaler = MinMaxScaler()
    minmaxscaler.fit(X_train[cols_num_minmax])

    # Standardize X_train
    X_train.loc[:, cols_num_std] = stdscaler.transform(X_train[cols_num_std])
    X_train.loc[:, cols_num_minmax] = minmaxscaler.transform(X_train[cols_num_minmax])

    # Standardize X_test
    X_test.loc[:, cols_num_std] = stdscaler.transform(X_test[cols_num_std])
    X_test.loc[:, cols_num_minmax] = minmaxscaler.transform(X_test[cols_num_minmax])

    logger.info("Fitting models.")
    # If selecting to use existing params, fit each individual model using those params
    if use_existing_params == True:
        logger.info("Using existing params in modelconfig file to fit random forest.")
        logger.debug("Random forest parameters: {}.".format(tuned_params["params_rf"]))
        model_rf = RandomForestRegressor(**tuned_params["params_rf"]).fit(
            X_train, y_train
        )
        logger.info("Fit random forest.")
        models_all.append(model_rf)
        logger.info("Using existing params in modelconfig file to fit GBM.")
        logger.debug("GBM parameters: {}.".format(tuned_params["params_gb"]))
        model_gb = GradientBoostingRegressor(**tuned_params["params_gb"]).fit(
            X_train, y_train
        )
        logger.info("Fit GBM.")
        models_all.append(model_gb)
        logger.info("Using existing params in modelconfig file to fit XGBoost.")
        logger.debug("XGBoost parameters: {}.".format(tuned_params["params_xgb"]))
        model_xgb = XGBRegressor(**tuned_params["params_xgb"]).fit(X_train, y_train)
        logger.info("Fit XGBoost.")
        models_all.append(model_xgb)
    # Otherwise, tune hyperparameters for each individual model
    else:
        logger.info("Tuning hyperparameters for random forest.")
        model_rf = RandomForestRegressor(**tuning_param_settings["rf_model_settings"])
        tuning_param_settings["param_grid_rf"]["max_features"] = eval(
            tuning_param_settings["param_grid_rf"]["max_features"]
        )
        model_rf = tune_model_grid_search(
            model_rf,
            X_train,
            y_train,
            tuning_param_settings["param_grid_rf"],
            grid_search_settings,
        )
        logger.info("Fit random forest.")
        models_all.append(model_rf)
        logger.info("Tuning hyperparameters for GBM.")
        model_gb = GradientBoostingRegressor(
            **tuning_param_settings["gb_model_settings"]
        )
        tuning_param_settings["param_grid_gb"]["learning_rate"] = eval(
            tuning_param_settings["param_grid_gb"]["learning_rate"]
        )
        model_gb = tune_model_grid_search(
            model_gb,
            X_train,
            y_train,
            tuning_param_settings["param_grid_gb"],
            grid_search_settings,
        )
        logger.info("Fit GBM.")
        models_all.append(model_gb)
        logger.info("Tuning hyperparameters for XGBoost.")
        model_xgb = XGBRegressor(**tuning_param_settings["xgb_model_settings"])
        tuning_param_settings["param_grid_xgb"]["eta"] = eval(
            tuning_param_settings["param_grid_xgb"]["eta"]
        )
        model_xgb = tune_model_grid_search(
            model_xgb,
            X_train,
            y_train,
            tuning_param_settings["param_grid_xgb"],
            grid_search_settings,
        )
        logger.info("Fit random forest.")
        models_all.append(model_xgb)

    # Evaluate all models
    logger.info("Evaluating models {}.".format(models_all))
    for model in models_all:
        evaluate_model(model, X_train, X_test, y_train, y_test)

    # Ensemble models into voting model and evaluate
    logger.info("Ensembling models.")
    models_all = [model for model in models_all if model is not None]
    if len(models_all) == 0:
        logger.warning("No models to ensemble.")
        ereg = None

    else:
        voting_model_settings["estimators"] = [
            (voting_model_settings["estimators"][i], models_all[i])
            for i in range(0, len(models_all))
        ]
        logger.debug("Settings for voting model: {}".format(voting_model_settings))
        ereg = VotingRegressor(**voting_model_settings)
        ereg.fit(X_train, y_train)
        evaluate_model(ereg, X_train, X_test, y_train, y_test)

        # Final TMO using all data
        ereg.fit(X, y)

    # Final scalers using all data
    stdscaler.fit(X[cols_num_std])
    minmaxscaler.fit(X[cols_num_minmax])

    return ereg, stdscaler, minmaxscaler


def tune_model_grid_search(model, X_train, y_train, grid, grid_settings):
    """Conduct randomized grid search to obtain optimal hyperparameters for model

    Args:
        model (:class:`sklearn.ensemble.[Regressor]` or :class:`xgboost.XGBRegressor`): regression model (random forest, gradient boosted tree, or xgboost)
        X_train (:class:`pandas.DataFrame`): training data features
        y_train (:class:`pandas.Series`): training data target variable
        grid (:obj:`dict`): hyperparameter grid settings to search over
        grid_settings (:obj:`dict`): settings for the randomized grid search

    Returns:
        :class:`sklearn.ensemble.[Regressor]` or :class:`xgboost.XGBRegressor`: fitted regression model using best parameters from grid search
    """

    try:
        # Conduct randomized grid search to find the best hyperparameters
        clf = RandomizedSearchCV(model, grid, **grid_settings)
        search = clf.fit(X_train, y_train)

        logger.debug("Best Parameters: {}.".format(search.best_params_))
        logger.debug("R2 using best parameters: {}.".format(search.best_params_))

        # Set model parameters with best parameters from randomized search
        logger.debug("Fitting model with best parameters.")
        model.set_params(**search.best_params_)
        model.fit(X_train, y_train)

        return model

    except Exception as e:
        logger.error(
            "Encountered error while conducting hyperparameter search for {}.".format(
                model
            )
        )
        logger.error(e)

        return None


def evaluate_model(model, X_train, X_test, y_train, y_test):
    """Generates predictions from model on test set and prints performance metrics

    Args:
        model (:class:`sklearn.ensemble.[Regressor]` or :class:`xgboost.XGBRegressor`): regression model (random forest, gradient boosted tree, or xgboost)
        X_train (:class:`pandas.DataFrame`): training data features
        X_test (:class:`pandas.DataFrame`): testing data features
        y_train (:class:`pandas.Series`): training data target variable
        y_test (:class:`pandas.Series`): testing data target variable
    """

    try:
        # Predict on both train and test set
        logger.debug("Predicting on test set.")
        pred_test = model.predict(X_test)

        # Score model
        logger.debug("Getting train r2, test r2, and RMSE.")
        train_r2 = model.score(X_train, y_train)
        test_r2 = model.score(X_test, y_test)
        rmse = math.sqrt(mean_squared_error(pred_test, y_test))

        logger.info("Performance metrics obtained for {} model.".format(model))
        print("Train R2:", train_r2)
        print("Test R2:", test_r2)
        print("RMSE:", rmse)

    except Exception as e:
        logger.error(
            "Encountered error whle predicting on the test set and getting performance metrics."
        )
        logger.error(e)
        pass
