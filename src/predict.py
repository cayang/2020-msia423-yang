import pandas as pd
import numpy as np
import math
import scipy.stats
import xgboost as xgb
import pickle as pkl
import yaml

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


def run_predict(X, modelconfig=None, model_file=None, enc_file=None, scalers_file=None):

    with open(modelconfig, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        # s3_objects = config["s3_objects"]
        model_file = config["model_files"]["MODEL_FILENAME_TMO"]
        enc_file = config["model_files"]["MODEL_FILENAME_ENCODER"]
        scalers_file = config["model_files"]["MODEL_FILENAME_SCALERS"]

    # Load model artifacts
    with open(model_file, "rb") as file:
        model = pkl.load(file)

    with open(enc_file, "rb") as file:
        enc = pkl.load(file)

    with open(scalers_file, "rb") as file:
        scalers = pkl.load(file)

    # Load in configs from yml file
    with open(modelconfig, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        COLS_NUM_STD = config["train_model"]["COLS_NUM_STD"]
        COLS_NUM_MINMAX = config["train_model"]["COLS_NUM_MINMAX"]
        COLS_CAT = config["train_model"]["COLS_CAT"]

    # Transform raw input data
    X = transform_input(X, enc, scalers, COLS_NUM_STD, COLS_NUM_MINMAX, COLS_CAT)

    # Generate prediction
    pred = generate_prediction(X, model)
    print(pred)

    return pred


def transform_input(X, enc, scalers, cols_std=None, cols_minmax=None, cols_enc=None):

    # Encode input variables
    df_enc = pd.DataFrame(
        enc.transform(X[cols_enc]).toarray(), columns=enc.get_feature_names(cols_enc),
    )
    X = X.join(df_enc).drop(columns=cols_enc)

    # Standardize input variables
    X.loc[:, cols_std] = scalers[0].transform(X[cols_std])
    X.loc[:, cols_minmax] = scalers[1].transform(X[cols_minmax])

    return X


def generate_prediction(X, model):

    return float(np.round(np.exp(model.predict(X)), 2))
