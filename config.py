import sys
import os
import pathlib
import datetime

# Getting the parent directory of this file. That will function as the project home.
HOME = pathlib.Path(sys.path[0])

# YAML filepath
YAML_CONFIG = HOME / "config" / "modelconfig.yml"

# Date indicating version of the file to be pulled
YEAR = 2019
MONTH = 11
DAY = 21
PULL_DATE = datetime.datetime(YEAR, MONTH, DAY)

# Source data URL
URL_LISTINGS = (
    "http://data.insideairbnb.com/united-states/il/chicago/"
    + PULL_DATE.strftime("%Y-%m-%d")
    + "/data/listings.csv.gz"
)

# S3 Bucket configs
S3_BUCKET = "nw-msia423-project-yang"
S3_OBJECT = "data/listings-raw.csv"

# RDS configs
RDS_DATABASE = "airbnbchi_db"

# Local data filepaths
DATA_PATH = HOME / "data"
DATA_FILENAME_RAW = DATA_PATH / (
    "listings-" + PULL_DATE.strftime("%Y%m%d") + "-raw.csv"
)
DATA_FILENAME_CLEAN = DATA_PATH / "listings-clean.csv"
DATA_FILENAME_NEIGHBORHOOD = DATA_PATH / "neighbourhoods.csv"
DATA_FILENAME_FEATURES = DATA_PATH / "features.csv"

# Local database filepaths
DATABASE_PATH = HOME / "data" / "airbnbchi.db"
