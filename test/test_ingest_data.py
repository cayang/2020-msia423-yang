import os
import pathlib
import requests
import logging
import logging.config
import pytest

import sys

sys.path.append("./")
sys.path.append("./src")

import src.ingest_data as ingest_data


def test_import_data_from_source():
    """Test that data is able to be downloaded from source"""

    if os.path.isfile(pathlib.Path("./test/test_listings_raw_ingested.csv")):
        os.remove(pathlib.Path("./test/test_listings_raw_ingested.csv"))

    url = "http://data.insideairbnb.com/united-states/il/chicago/2019-11-21/data/listings.csv.gz"
    ingest_data.import_data_from_source(
        url, "test_zip_file", ".", "test/test_listings_raw_ingested.csv"
    )

    assert os.path.isfile(pathlib.Path("./test/test_listings_raw_ingested.csv"))
    assert os.path.getsize("./test/test_listings_raw_ingested.csv") > 0
    os.remove(pathlib.Path("./test/test_listings_raw_ingested.csv"))


def test_import_data_from_source_bad():
    """Test that system exits if passed an invalid url"""

    if os.path.isfile(pathlib.Path("./test/test_listings_raw_ingested.csv")):
        os.remove(pathlib.Path("./test/test_listings_raw_ingested.csv"))

    url = "non_existant_url"

    with pytest.raises(SystemExit):
        ingest_data.import_data_from_source(
            url, "test_zip_file", ".", "test/test_listings_raw_ingested.csv"
        )
        assert (
            os.path.isfile(pathlib.Path("./test/test_listings_raw_ingested.csv"))
            == False
        )
