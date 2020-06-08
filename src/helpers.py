import logging
import logging.config
import boto3
import pandas as pd

from botocore.exceptions import ClientError

import config

logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def upload_to_s3(file_name, bucket, object_name=None):
    """Upload data file to S3 

    Args:
        file_name (str): file to upload
        bucket (str): S3 bucket name
        object_name (str, optional): S3 file path of uploaded file. 
            Defaults to None (where the entire file directory of `file_name` will be uploaded).
            Strongly recommend specifying the `object_name`
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    logger.info("Uploading file {} to bucket {} in S3.".format(file_name, bucket))
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logger.warning(
            "Could not upload file {} to bucket {} in S3.".format(file_name, bucket)
        )
        logger.error(e)
        return False
    return True


def read_from_s3(file_name, bucket, location):
    """Download data file from S3

    Args:
        file_name (str): S3 file name
        bucket (str): S3 bucket name
        location (str): local file path to download files to
    """

    # Download file
    s3_client = boto3.client("s3")

    logger.info("Downloading file {} from S3 to {}.".format(file_name, location))
    try:
        s3_client.download_file(bucket, file_name, location)
    except ClientError as e:
        logger.warning(
            "Could not download file {} from S3 to {}.".format(file_name, location)
        )
        logger.error(e)
        return False
    return True


def check_for_valid_cols(cols, df):
    """Checks that all coluns in cols list are in the dataframe

    Args:
        df (:class:`pandas.DataFrame`): listings data
        cols (:obj:`list`): list of columns expected in the `df`
    
    Returns:
        :obj:`list`: list of column names from `cols` in `df`
    """

    # Check for missing features in the data from what those expected
    missing_features = [f for f in cols if f not in df.columns.tolist()]

    # If there are missing features, update `feature_columns` to only include the non-missing names.
    if len(missing_features) > 0:
        logger.warning(
            "Dataset is missing {} expected columns {}".format(
                len(missing_features), missing_features
            )
        )
        cols = [f for f in cols if f not in missing_features]

    return cols
