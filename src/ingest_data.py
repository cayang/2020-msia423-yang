import os
import sys
import pandas as pd
import requests
import gzip
import boto3
import logging
import logging.config
import yaml

import config
from src.helpers import upload_to_s3

logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def run_ingest_data(args):
    """Run all steps to ingest data from source and upload raw data to S3

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - url: URL of source data
            - s3_bucket_name: name of the S3 bucket ot upload raw data to
            - data_path: local file path where raw data will be downloaded to
    """

    logger.info("Reading in configs from modelconfig.yml.")
    try:
        # Load in configs from yml file
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            s3_objects = config["s3_objects"]
            data_files = config["data_files"]
            zip_file_name = config["ingest_data"]["ZIP_FILE_NAME"]
    except KeyError:
        logger.error(
            "Encountered error when assigning variable from configurations file."
        )
        sys.exit(1)
    except (FileNotFoundError, IOError):
        logger.error("Encountered error in reading in the configurations file.")
        sys.exit(1)

    # Import data
    import_data_from_source(
        args.url, zip_file_name, args.data_path, data_files["DATA_FILENAME_RAW"]
    )

    # Upload to S3
    upload_to_s3(
        data_files["DATA_FILENAME_RAW"],
        args.s3_bucket_name,
        s3_objects["S3_OBJECT_DATA_RAW"],
    )

    # Remove raw data file
    logger.info("Removing zip file.")
    os.remove(data_files["DATA_FILENAME_RAW"])


def import_data_from_source(url, zip_filename, input_filepath, output_filename):
    """Import data source, unzip raw data file, and convert to CSV format

    Args:
        url (str): URL of the raw data source
        zip_filename (str): filename for the intermediate zip file that is downloaded from source
        input_filepath (str): file path where data will be downloaded to
        output_filename (str): file name of the output CSV file
    """

    # Get file from source
    logger.info("Obtaining data from {}.".format(url))
    try:
        r = requests.get(url)

        # Write out raw file
        with open("".join([input_filepath, "/", zip_filename]), "wb") as f:
            f.write(r.content)
        logger.info("Successfully downloaded raw data from {}.".format(url))

        # Unzip file and write raw data to CSV
        with gzip.open("".join([input_filepath, "/", zip_filename])) as f:
            file = pd.read_csv(f, low_memory=False)
            file.to_csv(
                output_filename, index=False,
            )
            # Remove zipped file
            os.remove("".join([input_filepath, "/", zip_filename]))
        logger.info(
            "Successfully unzipped raw data file and extracted CSV file to {}.".format(
                input_filepath
            )
        )

    except requests.exceptions.ConnectionError:
        logger.error("Encountered error while fetching data from {}.".format(url))
        sys.exit(1)

    except IOError:
        logger.error("Encountered error while attempting to write out raw data file.")
        sys.exit(1)
