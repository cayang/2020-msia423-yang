import os
import pathlib
import pandas as pd
import logging
import logging.config
import pytest

import sys

sys.path.append("./")
sys.path.append("./src")
sys.path.append("./data")

import src.clean_data as clean_data


def test_map_neighbourhoods():
    """Test that neighbourhood groups are mapped appropriately"""

    neighborhood = pd.read_csv("data/neighbourhoods.csv")
    data = pd.read_csv("test/test_listings-raw.csv")
    df = clean_data.map_neighbourhoods(data, neighborhood)
    assert "neighbourhood_group" in df.columns.tolist()


def test_map_neighbourhoods_bad():
    """Test that neighbourhood groups are not mapped if column is missing"""

    neighborhood = pd.read_csv("data/neighbourhoods.csv")
    data = pd.read_csv("test/test_bad_listings-raw.csv")
    df = clean_data.map_neighbourhoods(data, neighborhood)
    assert "neighbourhood_group" not in df.columns.tolist()


def test_drop_data():
    """Test that the appropriate columns and rows are dropped"""

    data = pd.read_csv("test/test_listings-raw.csv")
    drop_cols = ["listing_url", "host_url", "host_thumbnail_url", "host_picture_url"]
    df = clean_data.drop_data(data, drop_cols=drop_cols, target_col="reviews_per_month")
    assert (
        len([col for col in drop_cols if col in df.columns.tolist()]) == 0
        and df.shape[0] == data.shape[0] - 1
    )


def test_drop_data_bad():
    """Test that no data gets dropped when there is a key error"""

    data = pd.read_csv("test/test_listings-raw.csv")
    drop_cols = ["listing_url", "host_url", "host_thumbnail_url", "random_colname"]
    df = clean_data.drop_data(data, drop_cols=drop_cols, target_col="reviews_per_month")
    assert (
        len([col for col in drop_cols if col in df.columns.tolist()]) == 3
        and df.shape[0] == data.shape[0]
    )


def test_standardize_zipcode():
    """Test that zip code is standardized properly"""

    zip = "60657-0204"
    assert clean_data.standardize_zipcode(zip) == "60657"


def test_standardize_zipcode_bad():
    """Test bad zip code input"""

    zip = "606"
    with pytest.raises(Exception):
        assert clean_data.standardize_zipcode(zip) == None


def test_convert_price():
    """Test that price is properly converted"""

    price = "$1,000"
    assert clean_data.convert_price(price) == 1000.00


def test_convert_price_bad():
    """Test different format than expected price format"""

    price = "1000"
    assert clean_data.convert_price(price) == 1000.00


def test_convert_percentage():
    """Test that percentage is properly converted"""

    perc = "99%"
    assert clean_data.convert_percentage(perc) == 0.99


def test_convert_percentage_bad():
    """Test different format than expected percentage format"""

    perc = "99"
    assert clean_data.convert_percentage(perc) == 0.99
