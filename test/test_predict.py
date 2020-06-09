import os
import sys
import pathlib
import pandas as pd
import numpy as np
import pickle as pkl
import logging
import logging.config
import pytest

sys.path.append("./")
sys.path.append("./src")

import src.predict as predict


def test_transform_input():
    """Test input data transformation contains expected columns when categorical columns are one hot encoded"""

    with open("test/test_encoder.pkl", "rb") as file:
        enc = pkl.load(file)
    with open("test/test_scalers.pkl", "rb") as file:
        scalers = pkl.load(file)

    data = pd.read_csv("test/test_features.csv", nrows=2).drop(
        columns="reviews_per_month"
    )
    data_transformed = pd.read_csv("test/test_test-data.csv", nrows=2)

    COLS_NUM_STD = [
        "host_since_years",
        "host_listings_count",
        "amenities_count",
        "price",
        "security_deposit",
        "cleaning_fee",
    ]
    COLS_NUM_MINMAX = ["host_response_rate"]
    COLS_CAT = [
        "host_response_time",
        "property_type_cat",
        "room_type",
        "bed_type_cat",
        "neighbourhood_group",
        "cancellation_policy",
    ]

    assert (
        predict.transform_input(
            data, enc, scalers, COLS_NUM_STD, COLS_NUM_MINMAX, COLS_CAT
        ).columns.tolist()
        == data_transformed.columns.tolist()
    )


def test_transform_input_bad():
    """Test categorical variables are not one-hot encoded when the encoder is None"""

    enc = None
    with open("test/test_scalers.pkl", "rb") as file:
        scalers = pkl.load(file)

    data = pd.read_csv("test/test_features.csv", nrows=2).drop(
        columns="reviews_per_month"
    )
    data_transformed = pd.read_csv("test/test_test-data.csv", nrows=2)

    COLS_NUM_STD = [
        "host_since_years",
        "host_listings_count",
        "amenities_count",
        "price",
        "security_deposit",
        "cleaning_fee",
    ]
    COLS_NUM_MINMAX = ["host_response_rate"]
    COLS_CAT = [
        "host_response_time",
        "property_type_cat",
        "room_type",
        "bed_type_cat",
        "neighbourhood_group",
        "cancellation_policy",
    ]

    assert (
        predict.transform_input(
            data, enc, scalers, COLS_NUM_STD, COLS_NUM_MINMAX, COLS_CAT
        ).columns.tolist()
        != data_transformed.columns.tolist()
    )


def test_get_prediction():
    """Test predicted value is as expected"""

    input_data = pd.read_csv("test/test_input_data.csv")
    with open("test/test_model.pkl", "rb") as file:
        model = pkl.load(file)

    assert np.round(predict.generate_prediction(input_data, model), 2) == 0.48


def test_get_prediction_bad():
    """Test predicted value is None if input data is missing expected feature"""

    input_data = pd.read_csv("test/test_bad_input_data.csv")
    with open("test/test_model.pkl", "rb") as file:
        model = pkl.load(file)

    assert predict.generate_prediction(input_data, model) is None


def test_get_percentile():
    """Test calculated percentile is as expected"""

    arr = np.arange(1, 11)
    val = 9

    assert predict.generate_percentile(val, arr) == 90


def test_get_percentile_bad():
    """Test percentile is None if input data is invalid type"""

    arr = np.arange(1, 11)
    val = "9"

    assert predict.generate_percentile(val, arr) is None
