import os
import pathlib
import pandas as pd
import numpy as np
import datetime
import logging
import logging.config
import pytest

import sys

sys.path.append("./")
sys.path.append("./src")
sys.path.append("./data")

import src.generate_features as generate_features


def test_convert_truefalse():
    """Test that columns with t/f values are converted to boolean types."""

    data = pd.read_csv("test/test_listings-clean.csv")
    cols = ["host_is_superhost", "is_location_exact"]
    df = generate_features.convert_truefalse(data, cols)
    assert sum(np.isin(df["host_is_superhost"].to_numpy(), [0, 1])) == len(
        data
    ) and sum(np.isin(df["is_location_exact"].to_numpy(), [0, 1])) == len(data)


def test_convert_truefalse_bad():
    """Test that columns without t/f values are ignored and that the code does not break."""

    data = pd.read_csv("test/test_listings-clean.csv")
    cols = ["host_response_time", "is_location_exact"]
    df = generate_features.convert_truefalse(data, cols)
    assert sum(np.isin(df["is_location_exact"].to_numpy(), [0, 1])) == len(data)


def test_create_host_features():
    """Test that expected host feaures are created"""

    pull_date = datetime.datetime(2019, 11, 21)
    data = pd.read_csv("test/test_listings-clean.csv")
    df = generate_features.create_host_features(data, pull_date)
    assert "host_since_years" in df.columns.tolist()


def test_create_host_features_bad():
    """Test that host_since_years feature is not created when it contains bad data (invalid dates)"""

    pull_date = datetime.datetime(2019, 11, 21)
    data = pd.read_csv("test/test_bad_listings-clean.csv")
    df = generate_features.create_host_features(data, pull_date)
    assert "host_since_years" not in df.columns.tolist()


def test_create_property_features():
    """Test that expected property features are created"""

    data = pd.read_csv("test/test_listings-clean.csv")
    expected_cols = [
        "property_type_cat",
        "accommodates_cat",
        "bedrooms_cat",
        "bathrooms_cat",
        "beds_cat",
        "bed_type_cat",
        "guests_included_cat",
        "extra_people_cat",
        "amenities_count",
    ]
    df = generate_features.create_property_features(data)
    assert [col for col in expected_cols if col in df.columns.tolist()] == expected_cols


def test_create_property_features_bad():
    """Test that accommodates_cat feature is not created when it contains bad data (string instead of numeric)"""

    data = pd.read_csv("test/test_bad_listings-clean.csv")
    df = generate_features.create_property_features(data)
    assert "accommodates_cat" not in df.columns.tolist()


def test_create_booking_feature():
    """Test that expected booking features are created"""

    data = pd.read_csv("test/test_listings-clean.csv")
    expected_cols = ["cancellation_policy", "min_nights_cat", "max_nights_cat"]
    df = generate_features.create_booking_features(data)
    assert [col for col in expected_cols if col in df.columns.tolist()] == expected_cols


def test_create_booking_features_bad():
    """Test that cancellation_policy feature is not created when required columns are missing"""

    data = pd.read_csv("test/test_bad_listings-clean.csv")
    df = generate_features.create_booking_features(data)
    assert "cancellation_policy" not in df.columns.tolist()
