# IMPORTS
import os
import pathlib
import argparse
import pandas as pd
import boto3
import logging
import yaml
import subprocess

from botocore.exceptions import ClientError


def run_clean_data(args):
    """Import raw data files from S3, cleans data formats, and removes unused columns

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - data_file_raw: location of raw data file if already in local
            - keep_raw: specification of whether to save raw data CSV file to local
    """

    # Load configs from yml file
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        s3_objects = config["s3_objects"]
        data_files = config["data_files"]
        listing_dtypes = config["clean_data"]["LISTING_DTYPES"]
        drop_cols = config["clean_data"]["DROP_COLS"]

    # If not data file specified, download from S3 then read in raw data
    if args.data_file_raw is None:
        read_from_s3(
            s3_objects["S3_OBJECT_DATA_RAW"],
            args.s3_bucket_name,
            data_files["DATA_FILENAME_RAW"],
        )

    # Read in data from CSV
    df = pd.read_csv(
        data_files["DATA_FILENAME_RAW"], na_values=["NaN", "N/A"], dtype=listing_dtypes,
    )
    df_neighbourhood = pd.read_csv(data_files["DATA_FILENAME_NEIGHBORHOOD"])

    # Drop unused columns from
    df = df.drop(columns=drop_cols, axis=1)

    # Merge neighborhood group
    df = df.merge(
        df_neighbourhood,
        how="left",
        left_on="neighbourhood_cleansed",
        right_on="neighbourhood",
    ).drop(columns=["neighbourhood_cleansed", "neighbourhood"])

    # Drop observations where target variable is NA
    df = df.dropna(subset=["reviews_per_month"])

    # Clean variable types
    df = convert_variable_types(df)

    # Export clean data to CSV
    df.to_csv(data_files["DATA_FILENAME_CLEAN"])

    # Remove raw data from local if specified
    if args.keep_raw == False:
        os.remove(data_files["DATA_FILENAME_RAW"])


def read_from_s3(file_name, bucket, location):
    """Download data file from S3

    Args:
        file_name (str): S3 file name
        bucket (str): S3 bucket name
        location (str): location on local to download CSV file to
    """

    # Download file
    s3_client = boto3.client("s3")

    try:
        s3_client.download_file(bucket, file_name, location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def convert_variable_types(df):
    """Clean up variable types in the dataframe"""

    # Standardize zip codes as 5-digits
    df.loc[:, "zipcode"] = df["zipcode"].str[0:5]

    # Set price columns to numeric data types
    price_cols = [
        "price",
        "weekly_price",
        "monthly_price",
        "security_deposit",
        "cleaning_fee",
        "extra_people",
    ]

    for col in price_cols:
        df.loc[:, col] = df[col].str.replace(",", "").str[1:].astype(float)

    # Convert host_response_rate to numeric
    df.loc[:, "host_response_rate"] = (
        df["host_response_rate"].str[:-1].astype(float) / 100
    )

    return df
