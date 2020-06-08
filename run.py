import argparse
import logging
import logging.config

import config
from src.ingest_data import run_ingest_data
from src.clean_data import run_clean_data
from src.generate_features import run_generate_features
from src.create_db import run_create_db
from src.train_model import run_train_model

logging.config.fileConfig(config.LOGGING_CONFIG, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

if __name__ == "__main__":

    # Add parsers for all functions in the pipeline
    parser = argparse.ArgumentParser(description="Run model pipeline code")
    subparsers = parser.add_subparsers()

    # Sub-parser for uploading data to database
    sb_create_db = subparsers.add_parser(
        "create_db",
        description="Creates a database to store user input data and resulting predictions.",
    )
    sb_create_db.add_argument(
        "--config",
        "-c",
        default=config.YAML_CONFIG,
        help="Location of YAML file containing configurations for running model pipeline.",
    )
    sb_create_db.add_argument(
        "--truncate",
        "-t",
        default=False,
        type=bool,
        help="Specifies whether to delete an existing listings database table",
    )
    sb_create_db.add_argument(
        "--engine_string",
        "-e",
        default=config.SQLALCHEMY_DATABASE_URI,
        help="Engine string to create the SQL database.",
    )
    sb_create_db.set_defaults(func=run_create_db)

    # Sub-parser for ingesting data from source
    sb_ingest = subparsers.add_parser(
        "ingest", description="Ingest data from web source and upload raw file to S3."
    )
    sb_ingest.add_argument(
        "--config",
        "-c",
        default=config.YAML_CONFIG,
        help="Location of YAML file containing configurations for running model pipeline.",
    )
    sb_ingest.add_argument(
        "--url", "-u", default=config.URL_LISTINGS, help="URL of source data"
    )
    sb_ingest.set_defaults(func=run_ingest_data)
    sb_ingest.add_argument(
        "--s3_bucket_name",
        default=config.S3_BUCKET,
        help="Name of the S3 bucket to upload raw file to.",
    )
    sb_ingest.add_argument(
        "--data_path",
        default=config.DATA_PATH,
        help="Location of the data folder on local where the raw file will be downloaded.",
    )

    # Sub-parser for cleaning data
    sb_clean = subparsers.add_parser(
        "clean", description="Get raw data from S3, clean data, and save as CSV.",
    )
    sb_clean.add_argument(
        "--config",
        "-c",
        default=config.YAML_CONFIG,
        help="Location of YAML file containing configurations for running model pipeline.",
    )
    sb_clean.add_argument(
        "--s3_bucket_name",
        default=config.S3_BUCKET,
        help="Name of the S3 bucket to pull raw data from.",
    )
    sb_clean.add_argument(
        "--input",
        "-i",
        default=None,
        help="File name of the raw data file, if stored locally.",
    )
    sb_clean.add_argument(
        "--output",
        "-o",
        default=None,
        help="File name to save output cleaned data CSV file.",
    )
    sb_clean.add_argument(
        "--keep_raw",
        "-k",
        default=False,
        type=bool,
        help="Specifies whether to retain raw data file on the local filesystem.",
    )
    sb_clean.set_defaults(func=run_clean_data)

    # Sub-parser for generating features
    sb_features = subparsers.add_parser(
        "features",
        description="Generates and selects a subset of features in prepration for training the model.",
    )
    sb_features.add_argument(
        "--config",
        "-c",
        default=config.YAML_CONFIG,
        help="Location of YAML file containing configurations for running model pipeline.",
    )
    sb_features.add_argument(
        "--input", "-i", default=None, help="File name of the clean data file.",
    )
    sb_features.add_argument(
        "--output",
        "-o",
        default=None,
        help="File name to save output features data CSV file.",
    )
    sb_features.add_argument(
        "--pull_date",
        "-p",
        default=config.PULL_DATE_STR,
        help="As of date denoting the version of the dataset that was pulled from source.",
    )
    sb_features.set_defaults(func=run_generate_features)

    # Sub-parser for training model
    sb_train = subparsers.add_parser(
        "train", description="Creates trained model object."
    )
    sb_train.add_argument(
        "--config",
        "-c",
        default=config.YAML_CONFIG,
        help="Location of YAML file containing configurations for running model pipeline.",
    )
    sb_train.add_argument(
        "--input", "-i", default=None, help="File name of the features data file.",
    )
    sb_train.add_argument(
        "--output",
        "-o",
        default=None,
        help="File path to save output model artifacts pkl files. Must be an absolute folder path, not filename.",
    )
    sb_train.add_argument(
        "--use_existing_params",
        "-p",
        default=True,
        type=bool,
        help="Specifies whether to use existing hyperparameters in the modelconfig.yml (can speed up model training) file or to run the grid search.",
    )
    sb_train.add_argument(
        "--upload",
        "-u",
        default=True,
        type=bool,
        help="Specifies whether to upload trained model object and artifacts to S3 bucket.",
    )
    sb_train.add_argument(
        "--s3_bucket_name",
        default=config.S3_BUCKET,
        help="Name of the S3 bucket to upload model artifacts to.",
    )
    sb_train.set_defaults(func=run_train_model)

    args = parser.parse_args()
    args.func(args)
