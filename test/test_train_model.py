import os
import sys
import pathlib
import pandas as pd
import numpy as np
import math
import logging
import logging.config
import pytest

# Modeling packages
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestRegressor

sys.path.append("./")
sys.path.append("./src")
sys.path.append("./data")

import src.train_model as train_model


def test_get_imputed_values():
    """Test that all known NA values get imputed"""

    data = pd.read_csv("test/test_features.csv")
    data = data.drop(columns="reviews_per_month")

    dummy_cols = [
        "property_type_cat",
        "room_type",
        "bed_type_cat",
        "neighbourhood_group",
        "cancellation_policy",
    ]
    iter_imp_settings = {
        "max_iter": 10,
        "random_state": 423,
        "initial_strategy": "most_frequent",
    }
    HOST_RESPONSE_MAP = {
        "within an hour": 0,
        "within a few hours": 1,
        "within a day": 2,
        "a few days or more": 3,
    }
    expected_imputed_cols = [
        "cleaning_fee",
        "security_deposit",
        "host_response_rate",
        "host_response_time",
    ]
    df = train_model.get_imputed_values(
        data, dummy_cols, iter_imp_settings, HOST_RESPONSE_MAP
    )
    assert sum([df[col].isna().sum() for col in expected_imputed_cols]) == 0


def test_get_imputed_values_bad():
    """Test error in data type for Iterative Imputer"""

    data = pd.read_csv("test/test_features.csv")
    data = data.drop(columns="reviews_per_month")

    dummy_cols = [
        "property_type_cat",
        "room_type",
        "bed_type_cat",
        "neighbourhood_group",
        "cancellation_policy",
    ]
    iter_imp_settings = {
        "max_iter": 10,
        "random_state": 423,
        "initial_strategy": "most_frequent",
    }
    HOST_RESPONSE_MAP = {
        "within an hour": 0,
        "within a few hours": 1,
        "within a day": 2,
        "a few days or more": "3",
    }
    expected_imputed_cols = [
        "cleaning_fee",
        "security_deposit",
    ]
    expected_unimputed_cols = [
        "host_response_rate",
        "host_response_time",
    ]
    df = train_model.get_imputed_values(
        data, dummy_cols, iter_imp_settings, HOST_RESPONSE_MAP
    )
    assert sum([df[col].isna().sum() for col in expected_imputed_cols]) == 0
    assert sum([df[col].isna().sum() for col in expected_unimputed_cols]) > 0


def test_encode_variables():
    """Test categorical variables are one-hot encoded"""

    data = pd.read_csv("test/test_features.csv")
    enc_cols = [
        "bed_type_cat",
    ]
    df, enc = train_model.encode_variables(data, enc_cols)
    expected_enc_cols = ["bed_type_cat_Real Bed"]
    assert [
        col for col in expected_enc_cols if col in df.columns.tolist()
    ] == expected_enc_cols
    assert str(type(enc)) == "<class 'sklearn.preprocessing._encoders.OneHotEncoder'>"


def test_encode_variables_bad():
    """Test that code exits if features can't be one-hot encoded, since then model can't run"""

    data = pd.read_csv("test/test_features.csv")
    enc_cols = None
    with pytest.raises(SystemExit):
        df, enc = train_model.encode_variables(data, enc_cols)
        assert df is None
        assert enc is None


def test_tune_model_grid_search():
    """Test model tuning process returns the model"""

    X_train = pd.read_csv("test/test_train-data.csv")
    y_train = pd.read_csv("test/test_train-labels.csv")
    model = RandomForestRegressor(random_state=423)
    param_grid = {
        "n_estimators": [50, 100, 150, 200, 250, 300, 350, 400, 450, 500],
        "max_features": np.arange(3, int(math.sqrt(X_train.shape[1])) + 1),
        "min_samples_split": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "min_samples_leaf": [2, 3, 4, 5],
    }
    grid_search_settings = {
        "n_iter": 3,
        "random_state": 423,
        "n_jobs": -1,
        "scoring": "r2",
    }
    model = train_model.tune_model_grid_search(
        model, X_train, y_train, param_grid, grid_search_settings
    )
    assert (
        str(type(model)) == "<class 'sklearn.ensemble._forest.RandomForestRegressor'>"
    )


def test_tune_model_grid_search_bad():
    """Test model tuning process returns none if there is bad input"""

    X_train = pd.read_csv("test/test_train-data.csv")
    y_train = pd.read_csv("test/test_train-labels.csv")
    model = RandomForestRegressor(random_state=423)
    param_grid = {
        "n_estimators": str([50, 100, 150, 200, 250, 300, 350, 400, 450, 500]),
        "max_features": np.arange(3, int(math.sqrt(X_train.shape[1])) + 1),
        "min_samples_split": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "min_samples_leaf": [2, 3, 4, 5],
    }
    grid_search_settings = {
        "n_iter": 3,
        "random_state": 423,
        "n_jobs": -1,
        "scoring": "r2",
    }
    model = train_model.tune_model_grid_search(
        model, X_train, y_train, param_grid, grid_search_settings
    )
    assert model is None


def test_evaluate_model():
    """Test model evaluation returns desired metrics"""

    X_train = pd.read_csv("test/test_train-data.csv")
    y_train = pd.read_csv("test/test_train-labels.csv")
    X_test = pd.read_csv("test/test_test-data.csv")
    y_test = pd.read_csv("test/test_test-labels.csv")

    model = RandomForestRegressor(random_state=423).fit(X_train, y_train)

    metrics = train_model.evaluate_model(model, X_train, X_test, y_train, y_test)

    assert (
        "Train R2" in metrics.columns.tolist()
        and "Test R2" in metrics.columns.tolist()
        and "Test RMSE" in metrics.columns.tolist()
    )


def test_evaluate_model_bad():
    """Test model evaluation returns none with errors in evaluation"""

    X_train = pd.read_csv("test/test_train-data.csv")
    y_train = pd.read_csv("test/test_train-labels.csv")
    X_test = pd.read_csv("test/test_test-data.csv")
    # Define random vector of size 10, when evaluation expects 20
    y_test = np.random.rand(10) * 5

    model = RandomForestRegressor(random_state=423).fit(X_train, y_train)

    metrics = train_model.evaluate_model(model, X_train, X_test, y_train, y_test)

    assert metrics is None
