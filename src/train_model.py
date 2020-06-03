import pandas as pd
import numpy as np
import math
import scipy
import xgboost as xgb
import pickle as pkl
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

# User-written odules
from src.ingest_data import upload_to_s3


def run_train_model(args):
    """Perform model training (imputation, hyperparameter search) and obtain trained model object

    Args:
        # TODO:
        args ([type]): [description]
    """

    # Load in configs from yml file
    with open(args.config.YAML_CONFIG, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

        # Feature lists and dictionaries for transformations
        HOST_RESPONSE_MAP = config["train_model"]["HOST_RESPONSE_MAP"]
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

    # Read in features dataset
    df = pd.read_csv(args.config.DATA_FILENAME_FEATURES)

    # Impute missing values
    dummy_cols = [col for col in COLS_CAT if col not in IMPUTE_COLS]
    df_imputed = get_imputed_values(
        df, dummy_cols, iter_imp_settings, HOST_RESPONSE_MAP
    )
    df.loc[:, IMPUTE_COLS] = df_imputed[IMPUTE_COLS]

    # One hot encode all categorical variables to get final dataframe for model development
    df_model, enc = encode_variables(df, COLS_CAT)

    # Develop trained model object
    tmo, stdscaler, minmaxscaler = get_trained_model_object(
        df_model,
        COLS_NUM_STD,
        COLS_NUM_MINMAX,
        train_test_settings,
        tuning_param_settings,
        grid_search_settings,
        voting_model_settings,
        tuned_params=tuned_params,
        use_existing_params=args.use_existing_params,
    )

    # Output model and encoder to pkl file
    with open(args.config.MODEL_FILENAME_TMO, "wb") as file:
        pkl.dump(tmo, file)
    with open(args.config.MODEL_FILENAME_ENCODER, "wb") as file:
        pkl.dump(enc, file)
    with open(args.config.MODEL_FILENAME_SCALERS, "wb") as file:
        pkl.dump((stdscaler, minmaxscaler), file)

    # Upload to S3 if chosen
    if args.upload:
        upload_to_s3(
            str(args.config.MODEL_FILENAME_TMO),
            args.config.S3_BUCKET,
            args.config.S3_OBJECT_MODEL_TMO,
        )
        upload_to_s3(
            str(args.config.MODEL_FILENAME_ENCODER),
            args.config.S3_BUCKET,
            args.config.S3_OBJECT_MODEL_ENCODER,
        )
        upload_to_s3(
            str(args.config.MODEL_FILENAME_SCALERS),
            args.config.S3_BUCKET,
            args.config.S3_OBJECT_MODEL_SCALERS,
        )


def get_imputed_values(df, dummy_cols, settings, host_response_map):
    """Imputes missing values for features with known missing values.

    Args:
        df ([type]): [description]
        dummy_cols ([type]): [description]
        settings ([type]): [description]
        host_response_map ([type]): [description]

    Returns:
        [type]: [description]
    """

    # One hot encode nominal categorical variables for iterative imputer
    df = pd.get_dummies(df, columns=dummy_cols, drop_first=True)

    # Use median for security_deposit and cleaning_fee
    num_values = {
        "cleaning_fee": df["cleaning_fee"].median(),
        "security_deposit": df["security_deposit"].median(),
    }
    df = df.fillna(value=num_values)

    # Map host_response_time to numerical values and drop original column
    df.loc[:, "host_response_time_code"] = df["host_response_time"].map(
        host_response_map
    )
    df = df.drop(columns="host_response_time")

    # Set imputer settings to impute host_response_rate and host_response_time_code
    imp = IterativeImputer(**settings)

    # Define dataframe for imputation, excluding response variable
    df_for_imp = df.loc[:, ~df.columns.isin(["reviews_per_month"])]

    # Get column names
    colnames = df_for_imp.columns.tolist()

    # Final imputed dataframe, excluding response variable
    df_imp = pd.DataFrame(imp.fit_transform(df_for_imp), columns=colnames)

    # Round the imputed values
    df_imp.loc[:, "host_response_rate"] = round(
        np.minimum(df_imp["host_response_rate"], 1.0), 2
    )
    df_imp.loc[:, "host_response_time_code"] = round(
        df_imp["host_response_time_code"], 0
    ).astype(int)

    # Invert the host response time map
    inv_map = {v: k for k, v in host_response_map.items()}
    df_imp.loc[:, "host_response_time"] = df_imp["host_response_time_code"].map(inv_map)

    return df_imp


def encode_variables(df, cols):

    # Define encoder
    enc = OneHotEncoder(drop="first")

    # Fit encoder to categorical columns
    enc.fit(df[cols])

    # Transform categorical predictors
    df_enc = pd.DataFrame(
        enc.transform(df[cols]).toarray(), columns=enc.get_feature_names(cols)
    )

    # Merge one-hot encoded columns with dataframe and drop original features
    df = df.join(df_enc).drop(columns=cols)

    return df, enc


def get_trained_model_object(
    df,
    cols_num_std,
    cols_num_minmax,
    train_test_settings,
    tuning_param_settings,
    grid_search_settings,
    voting_model_settings,
    tuned_params=None,
    use_existing_params=False,
):

    # List to contain all models fitted
    models_all = []

    # Split into train / test set
    X = df[[col for col in df.columns if col != "reviews_per_month"]]
    y = df["reviews_per_month"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, **train_test_settings)
    print("Train data shape:", X_train.shape)
    print("Test data shape:", X_test.shape)

    # Standardize predictors by defining scalers
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

    # TODO: Move to separate functions?
    # If selecting to use existing params, fit each individual model using those params
    if use_existing_params == True:
        model_rf = RandomForestRegressor(**tuned_params["params_rf"]).fit(
            X_train, y_train
        )
        models_all.append(model_rf)
        model_gb = GradientBoostingRegressor(**tuned_params["params_gb"]).fit(
            X_train, y_train
        )
        models_all.append(model_gb)
        model_xgb = XGBRegressor(**tuned_params["params_xgb"]).fit(X_train, y_train)
        models_all.append(model_xgb)
    # Otherwise, tune hyperparameters for each individual model
    else:
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
        models_all.append(model_rf)
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
        models_all.append(model_gb)
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
        models_all.append(model_xgb)

    # Evaluate all models
    for model in models_all:
        evaluate_model(model, X_train, X_test, y_train, y_test)

    # Ensemble models into voting model and evaluate
    voting_model_settings["estimators"] = [
        (voting_model_settings["estimators"][i], models_all[i])
        for i in range(0, len(models_all))
    ]
    ereg = VotingRegressor(**voting_model_settings)
    ereg.fit(X_train, y_train)
    evaluate_model(ereg, X_train, X_test, y_train, y_test)

    # Final TMO and model artifacts using all data
    stdscaler.fit(X[cols_num_std])
    minmaxscaler.fit(X[cols_num_minmax])
    ereg.fit(X, y)

    return ereg, stdscaler, minmaxscaler


def tune_model_grid_search(model, X_train, y_train, grid, grid_settings):

    # Conduct randomized grid search to find the best hyperparameters
    clf = RandomizedSearchCV(model, grid, **grid_settings)
    search = clf.fit(X_train, y_train)

    print("Best Parameters:", search.best_params_)
    print("R2:", search.best_score_)

    # Set model parameters with best parameters from randomized search
    model.set_params(**search.best_params_)
    model.fit(X_train, y_train)

    return model


def evaluate_model(model, X_train, X_test, y_train, y_test):

    # Predict on both train and test set
    pred_test = model.predict(X_test)

    # Score model
    train_r2 = model.score(X_train, y_train)
    test_r2 = model.score(X_test, y_test)
    rmse = math.sqrt(mean_squared_error(pred_test, y_test))

    print("Train R2:", train_r2)
    print("Test R2:", test_r2)
    print("RMSE:", rmse)
