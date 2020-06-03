import os
import argparse
import pandas as pd
import requests
import gzip
import boto3
import logging
import yaml

from botocore.exceptions import ClientError


def run_ingest_data(args):
    """Run all steps to ingest data from source and upload raw data to S3

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - url: URL of source data
    """

    # Load in configs from yml file
    with open(args.config.YAML_CONFIG, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        zip_file_name = config["ingest_data"]["ZIP_FILE_NAME"]

    # Import data
    import_data_from_source(
        args.url, zip_file_name, args.config.DATA_PATH, args.config.DATA_FILENAME_RAW
    )

    # Upload to S3
    upload_to_s3(
        str(args.config.DATA_FILENAME_RAW),
        args.config.S3_BUCKET,
        args.config.S3_OBJECT_DATA_RAW,
    )

    # Remove raw data file
    os.remove(args.config.DATA_FILENAME_RAW)


def import_data_from_source(url, zip_filename, input_filepath, output_filename):
    """Import data source, unzip raw data file, and convert to CSV format

    Args:
        url (str): URL of the raw data source
        zip_filename(str): filename for the intermediate zip file that is downloaded from source
        output_filename (str): file path and name of the output CSV file
    """

    # Get file from source
    r = requests.get(url)

    # Write out raw file
    with open(input_filepath / zip_filename, "wb") as f:
        f.write(r.content)

    # Unzip file and write raw data to CSV
    # TODO: Write file to text file
    with gzip.open(input_filepath / zip_filename) as f:
        file = pd.read_csv(f, low_memory=False)
        file.to_csv(
            output_filename, index=False,
        )

        # Remove zipped file
        os.remove(input_filepath / zip_filename)


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
