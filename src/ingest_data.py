import os
import argparse
import pandas as pd
import requests
import gzip
import boto3
import logging
import yaml

from botocore.exceptions import ClientError

from config import (
    HOME,
    URL_LISTINGS,
    YAML_CONFIG,
    S3_BUCKET,
    S3_OBJECT,
    DATA_PATH,
    DATA_FILENAME_RAW,
    PULL_DATE,
)


def run_ingest_data(args):
    """Run all steps to ingest data from source and upload raw data to S3

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - url: URL of source data
    """

    # Load in configs from yml file
    with open(YAML_CONFIG, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        zip_file_name = config["ingest_data"]["ZIP_FILE_NAME"]

    # Import data
    import_data_from_source(args.url, zip_file_name, DATA_FILENAME_RAW)

    # Upload to S3
    upload_to_s3(
        str(DATA_FILENAME_RAW), S3_BUCKET, S3_OBJECT,
    )

    # Remove raw data file
    os.remove(DATA_FILENAME_RAW)


def import_data_from_source(url, zip_filename, output_filename):
    """Import data source, unzip raw data file, and convert to CSV format

    Args:
        url (str): URL of the raw data source
        zip_filename(str): filename for the intermediate zip file that is downloaded from source
        output_filename (str): file path and name of the output CSV file
    """

    # Get file from source
    r = requests.get(url)

    # Write out raw file
    with open(DATA_PATH / zip_filename, "wb") as f:
        f.write(r.content)

    # Unzip file and write raw data to CSV
    with gzip.open(DATA_PATH / zip_filename) as f:
        file = pd.read_csv(f, low_memory=False)
        file.to_csv(
            output_filename, index=False,
        )

        # Remove zipped file
        os.remove(DATA_PATH / zip_filename)


def upload_to_s3(file_name, bucket, object_name=None):
    """Upload data file to S3 

    Args:
        file_name (str): file to upload
        bucket (str): S3 bucket name
        object_name (str, optional): S3 filepath of uploaded file. 
            Defaults to None (where the entire file directory of `file_name` will be uploaded).
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client("s3")
    try:
        # TODO: Add response when adding logging
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":

    # Add parsers for running ingest_data
    parser = argparse.ArgumentParser(description="Run run_ingest_data")
    subparsers = parser.add_subparsers()

    # Sub-parser
    sb_ingest = subparsers.add_parser(
        "ingest", description="Ingest data from web source and upload raw file to S3."
    )
    sb_ingest.add_argument(
        "--url", "-u", default=URL_LISTINGS, help="URL of source data"
    )
    sb_ingest.set_defaults(func=run_ingest_data)

    args = parser.parse_args()
    args.func(args)
