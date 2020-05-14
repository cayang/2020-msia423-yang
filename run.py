import argparse

import config
from src.ingest_data import run_ingest_data
from src.clean_data import run_clean_data
from src.generate_features import run_generate_features
from src.create_db import run_create_db

if __name__ == "__main__":

    # Add parsers for all functions in the pipeline
    parser = argparse.ArgumentParser(description="Run model pipeline code")
    subparsers = parser.add_subparsers()

    # Sub-parser for ingesting data from source
    sb_ingest = subparsers.add_parser(
        "ingest", description="Ingest data from web source and upload raw file to S3."
    )
    sb_ingest.add_argument(
        "--config", default=config.YAML_CONFIG, help="Location of configuration YAML"
    )
    sb_ingest.add_argument(
        "--url", default=config.URL_LISTINGS, help="URL of source data"
    )
    sb_ingest.set_defaults(func=run_ingest_data)

    # Sub-parser for cleaning data
    sb_clean = subparsers.add_parser(
        "clean", description="Get raw data from S3, clean data, and save as CSV.",
    )
    sb_clean.add_argument(
        "--config", default=config.YAML_CONFIG, help="Location of configuration YAML"
    )
    sb_clean.add_argument(
        "--data_file_raw", default=None, help="Location of the raw data file"
    )
    sb_clean.add_argument(
        "--keep_raw",
        default=True,
        type=bool,
        help="Specifies whether to retain raw data file on local filesystem",
    )
    sb_clean.set_defaults(func=run_clean_data)

    # Sub-parser for generating features
    sb_features = subparsers.add_parser(
        "features",
        description="Generates and selects a subset of features in prepration for training the model.",
    )
    sb_features.add_argument(
        "--config", default=config.YAML_CONFIG, help="Location of configuration YAML"
    )
    sb_features.add_argument(
        "--select_features",
        default=False,
        type=bool,
        help="Specifies whether to manually specify features to keep",
    )
    sb_features.set_defaults(func=run_generate_features)

    # Sub-parser for uploading data to database
    sb_create_db = subparsers.add_parser(
        "create_db", description="Creates a database to store feature data."
    )
    sb_create_db.add_argument(
        "--config", default=config.YAML_CONFIG, help="Location of configuration YAML"
    )
    sb_create_db.add_argument(
        "--local",
        default=False,
        type=bool,
        help="Creates SQL Lite database locally, if true (defaults to False)",
    )
    sb_create_db.set_defaults(func=run_create_db)

    args = parser.parse_args()
    args.func(args)
