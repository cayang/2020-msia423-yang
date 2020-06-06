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
PULL_DATE_STR = datetime.datetime(YEAR, MONTH, DAY).strftime("%Y-%m-%d")

# Source data URL
URL_LISTINGS = (
    "http://data.insideairbnb.com/united-states/il/chicago/"
    + PULL_DATE_STR
    + "/data/listings.csv.gz"
)

# Local filepaths
DATA_PATH = HOME / "data"
DATABASE_PATH = HOME / "data" / "airbnbchi.db"

# S3 Bucket configs
S3_BUCKET = "nw-msia423-project-yang"

# Connection string
DB_HOST = os.environ.get("MYSQL_HOST")
DB_PORT = os.environ.get("MYSQL_PORT")
DB_USER = os.environ.get("MYSQL_USER")
DB_PW = os.environ.get("MYSQL_PASSWORD")
DATABASE = os.environ.get("MYSQL_DATABASE")
DB_DIALECT = "mysql+pymysql"
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

if DATABASE is None:
    DATABASE = "airbnbchi_db"  # Default RDS database

print(SQLALCHEMY_DATABASE_URI)
print(DB_HOST)
if SQLALCHEMY_DATABASE_URI is not None:
    pass
elif DB_HOST is None:
    SQLALCHEMY_DATABASE_URI = "sqlite:////{}".format(DATABASE_PATH)
else:
    SQLALCHEMY_DATABASE_URI = "{dialect}://{user}:{pw}@{host}:{port}/{db}".format(
        dialect=DB_DIALECT,
        user=DB_USER,
        pw=DB_PW,
        host=DB_HOST,
        port=DB_PORT,
        db=DATABASE,
    )
print(SQLALCHEMY_DATABASE_URI)

# Flask configs
DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5000
APP_NAME = "airbnbchi"
HOST = "0.0.0.0"
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 10
