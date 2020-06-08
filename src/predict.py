import sys
import pandas as pd
import numpy as np
import math
import xgboost as xgb
import pickle as pkl
import logging
import logging.config
import yaml

from scipy import stats
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

import config
from src.helpers import read_from_s3, check_for_valid_cols


logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def run_predict(
    X,
    modelconfig=None,
    model_file=None,
    enc_file=None,
    scalers_file=None,
    s3_bucket_name=None,
    percentile=True,
):
    """Generate the predicted number of reviews per month and percentile rank given app user input

    Args:
        X (:class:`pandas.DataFrame`): dataframe containing user's input
        modelconfig (str, optional): location of the YAML config file. Defaults to None.
        model_file (str, optional): local file path of the trained model object. Defaults to None (checks the modelconfig file).
        enc_file (str, optional): local file path of the encoders. Defaults to None (checks the modelconfig file).
        scalers_file (str, optional): local file path of the scalers. Defaults to None (checks the modelconfig file).
        s3_bucket_name (str, optional): name of the S3 bucket to obtain model, encoder, and scaler artifacts. Defaults to None.
            If not None, then model artifacts will be pulled from S3. Otherwise, will search local file paths for objects.
        percentile (bool, optional): whether to return percentile rank score. Defaults to True.

    Returns:
        pred (float): predicted number of reviews per month
        perc (float): percentile rank of predicted value relative to existing listins
    """

    logger.info("Reading in configs from modelconfig.yml.")
    try:
        with open(modelconfig, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            s3_objects = config["s3_objects"]
            # Load in model artifacts
            if model_file is None:
                model_file = config["model_files"]["MODEL_FILENAME_TMO"]
            if enc_file is None:
                enc_file = config["model_files"]["MODEL_FILENAME_ENCODER"]
            if scalers_file is None:
                scalers_file = config["model_files"]["MODEL_FILENAME_SCALERS"]
            # Load in dataset configurations
            COLS_NUM_STD = config["train_model"]["COLS_NUM_STD"]
            COLS_NUM_MINMAX = config["train_model"]["COLS_NUM_MINMAX"]
            COLS_CAT = config["train_model"]["COLS_CAT"]
            if percentile == True:
                data_file = config["data_files"]["DATA_FILENAME_FEATURES"]
                target_col = config["TARGET_COL"]
    except KeyError:
        logger.error(
            "Encountered error when assigning variable from configurations file."
        )
        sys.exit(1)
    except (FileNotFoundError, IOError):
        logger.error("Encountered error in reading in the configurations file.")
        sys.exit(1)

    if s3_bucket_name is not None:
        logger.info("Downloading model artifacts from S3.")
        read_from_s3(s3_objects["S3_OBJECT_MODEL_TMO"], s3_bucket_name, model_file)
        read_from_s3(s3_objects["S3_OBJECT_MODEL_ENCODER"], s3_bucket_name, enc_file)
        read_from_s3(
            s3_objects["S3_OBJECT_MODEL_SCALERS"], s3_bucket_name, scalers_file
        )

    # Load model artifacts
    try:
        logger.info("Loading in trained model object from {}.".format(model_file))
        with open(model_file, "rb") as file:
            model = pkl.load(file)

        logger.info("Loading in encoder object from {}.".format(enc_file))
        with open(enc_file, "rb") as file:
            enc = pkl.load(file)

        logger.info("Loading in scalers objects from {}.".format(scalers_file))
        with open(scalers_file, "rb") as file:
            scalers = pkl.load(file)
    except KeyError:
        logger.error("Encountered error when loading in model artifacts.")
        sys.exit(1)
    except (FileNotFoundError, IOError):
        logger.error("Encountered error when reading in model artifacts.")
        sys.exit(1)

    # Check that all features expected are in the dataframe
    logger.debug("Checking that expected feature are in the input dataframe.")
    COLS_NUM_STD = check_for_valid_cols(COLS_NUM_STD, X)
    COLS_NUM_MINMAX = check_for_valid_cols(COLS_NUM_MINMAX, X)
    COLS_CAT = check_for_valid_cols(COLS_CAT, X)

    # Transform raw input data
    logger.debug("Performing transformations on input data.")
    X = transform_input(X, enc, scalers, COLS_NUM_STD, COLS_NUM_MINMAX, COLS_CAT)

    # Generate prediction
    logger.debug("Generating prediction.")
    pred = generate_prediction(X, model)

    # Generate percentile
    if percentile == True:
        logger.debug("Calculating percentile rank.")
        try:
            y = pd.read_csv(data_file)[target_col]
            perc = generate_percentile(pred, y)
        except:
            logger.error(
                "Encountered error when loading in actual reviews per month data."
            )
            perc = None
    else:
        perc = None

    return pred, perc


def transform_input(X, enc, scalers, cols_std=None, cols_minmax=None, cols_enc=None):
    """Transform input data

    Args:
        X (:class:`pandas.DataFrame`): dataframe containing user's input
        enc (:class:`sklearn.preprocessing.OneHotEncoder`): encoder to transform categorical variables
        scalers (:obj:`list`: [:class:`sklearn.preprocessing.StandardScaler`, :class:`sklearn.preprocessing.MinMAxScaler`]): 
            scaler objects to transform numeric variables
        cols_std (:obj:`list`, optional): list of columns to standardize. Defaults to None.
        cols_minmax (:obj:`list`, optional): list of columns to standardize using minmax scaler. Defaults to None.
        cols_enc (:obj:`list`, optional): list of columns to one-hot encode. Defaults to None.

    Returns:
        :class:`pandas.DataFrame`: input dataframe with applied data transformations to be fed into TMO for prediction
    """

    # Encode input variables
    try:
        if cols_enc is None:
            logger.warning("No columns specified for one-hot encoding.")
            pass
        else:
            logger.debug("One-hot encoding features {}.".format(cols_enc))
            df_enc = pd.DataFrame(
                enc.transform(X[cols_enc]).toarray(),
                columns=enc.get_feature_names(cols_enc),
            )
            X = X.join(df_enc).drop(columns=cols_enc)
    except Exception as e:
        logger.error("Could not apply encoder to input dataframe.")
        logger.error(e)
        pass

    # Standardize input variables
    try:
        if cols_std is None:
            logger.warning("No columns specified for normalized standardization.")
            pass
        else:
            logger.debug("Normalizing features {}.".format(cols_std))
            X.loc[:, cols_std] = scalers[0].transform(X[cols_std])
    except Exception as e:
        logger.error("Could not apply normalized standardization to input dataframe.")
        logger.error(e)
        pass

    try:
        if cols_minmax is None:
            logger.warning("No columns specified for minmax standardization.")
        else:
            logger.debug("Minmax standardizing features {}.".format(cols_minmax))
            X.loc[:, cols_minmax] = scalers[1].transform(X[cols_minmax])
    except Exception as e:
        logger.error("Could not apply minmax standardization to input dataframe.")
        logger.error(e)
        pass

    return X


def generate_prediction(X, model):
    """Return predicted target value for input data

    Args:
        X (:class:`pandas.DataFrame`): input data to generate a prediction for
        model (:class:`sklearn.ensemble.VotingRegressor`): trained model object

    Returns:
        float: predicted target value
    """

    try:
        return float(np.round(np.exp(model.predict(X)), 2))
    except Exception as e:
        logger.error("Could not generate prediction.")
        logger.error(e)
        return None


def generate_percentile(pred, y):
    """Return percentile rank of predicted value relative to actual values

    Args:
        pred (float): predicted number of reviews per month
        y (:obj:`list`): list of actual reviews per month

    Returns:
        float: percentile rank
    """

    try:
        return np.round(stats.percentileofscore(y, pred), 2)
    except Exception as e:
        logger.error("Could not calculate percentile rank.")
        logger.error(e)
        return None
