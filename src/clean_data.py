import os
import sys
import pathlib
import pandas as pd
import re
import boto3
import logging
import logging.config
import yaml

from botocore.exceptions import ClientError

import config
from src.helpers import read_from_s3

logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def run_clean_data(args):
    """Import raw data files from S3, cleans data formats, and removes unused columns

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - s3_bucket_name: name of the S3 bucket where raw data file is located
            - input: local file path of raw data file, if already in local
            - output: local file path to output the cleaned data
            - keep_raw: specification of whether to save raw data CSV file to local
    """

    logger.info("Reading in configs from modelconfig.yml.")
    try:
        # Load configs from yml file
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            s3_objects = config["s3_objects"]
            data_files = config["data_files"]
            listing_dtypes = config["clean_data"]["LISTING_DTYPES"]
            drop_cols = config["clean_data"]["DROP_COLS"]
            target_col = config["TARGET_COL"]
    except KeyError:
        logger.error(
            "Encountered error when assigning variable from configurations file."
        )
        sys.exit(1)
    except (FileNotFoundError, IOError):
        logger.error("Encountered error in reading in the configurations file.")
        sys.exit(1)

    # If input raw data file not specified, download from S3
    if args.input is None:
        logger.info("Fetching raw data from S3 bucket {}.".format(args.s3_bucket_name))
        read_from_s3(
            s3_objects["S3_OBJECT_DATA_RAW"],
            args.s3_bucket_name,
            data_files["DATA_FILENAME_RAW"],
        )
        raw_file = data_files["DATA_FILENAME_RAW"]
    else:
        raw_file = args.input

    # Read in raw data and neighbourhood mapping file from CSV
    logger.info("Reading in raw data and neighbourhoods CSV files.")
    try:
        df = pd.read_csv(raw_file, na_values=["NaN", "N/A"], dtype=listing_dtypes)
        logger.info(
            "Raw dataset contains {} rows and {} columns.".format(
                df.shape[0], df.shape[1]
            )
        )
    except (FileNotFoundError, IOError):
        logger.error("Encountered error in reading in the raw data CSV file.")
        sys.exit(1)
    try:
        df_neighbourhood = pd.read_csv(data_files["DATA_FILENAME_NEIGHBORHOOD"])
    except (FileNotFoundError, IOError):
        logger.warning("Encountered error in reading in the neighbourhoods.csv file.")
        df_neighbourhood = None
        pass

    # Perform cleaning steps
    logger.debug("Dropping invalid data.")
    df = drop_data(df, drop_cols, target_col)
    logger.debug("Reading in neighbourhood mapping file.")
    if df_neighbourhood is not None:
        df = map_neighbourhoods(df, df_neighbourhood)
    logger.debug("Converting variable types in raw data.")
    df = convert_variable_types(df)

    # Export clean data to CSV
    if args.output is None:
        df.to_csv(data_files["DATA_FILENAME_CLEAN"], index=False)
        logger.info(
            "Exported cleaned data file to {}".format(data_files["DATA_FILENAME_CLEAN"])
        )
    else:
        df.to_csv(args.output, index=False)
        logger.info("Exported cleaned data file to {}".format(args.output))

    # Remove raw data from local if specified
    if args.input is None and args.keep_raw == False:
        logger.info("Removing raw data file {}".format(raw_file))
        os.remove(raw_file)


def map_neighbourhoods(df, df_neighbourhood):
    """Map the neighbourhoods from the data file to neighbourhood groups

    Args:
        df (:class:`pandas.DataFrame`): listings data
        df_neighbourhood (:class:`pandas.DataFrame`): neighbourhood group mappings

    Returns:
        :class:`pandas.DataFrame`: listings data with neighbourhood group mapped
    """

    try:
        df = df.merge(
            df_neighbourhood,
            how="left",
            left_on="neighbourhood_cleansed",
            right_on="neighbourhood",
        ).drop(columns=["neighbourhood_cleansed", "neighbourhood"])
        logger.info(
            "Mapped neighbourhood group to neighbourhoods in the listings data. Dropping `neighbourhood_cleansed` column."
        )
    except KeyError:
        logger.warning(
            "Could not map neighbourhood groups due to key error. Please double check the column names."
        )
        pass

    return df


def drop_data(df, drop_cols=None, target_col="reviews_per_month"):
    """Drop unused columns from the dataframe and records where target variable is NA

    Args:
        df (:class:`pandas.DataFrame`): listings data
        drop_cols (:obj:`list`, optional): list of columns to drop. Defaults to None.
        target_col (str, optional): target column for which NA rows will be dropped. Defaults to "reviews_per_month".

    Returns:
        :class:`pandas.DataFrame`: listings data with unused columns and invalid rows dropped
    """

    try:
        # Drop unused columns from the dataframe
        df = df.drop(columns=drop_cols, axis=1)
        logger.info(
            "Removed {} columns from raw data file: {}".format(
                len(drop_cols), drop_cols
            )
        )

        # Drop observations where target variable is NA
        begin_size = df.shape[0]
        num_na = df[target_col].isna().sum()
        df = df.dropna(subset=[target_col])
        end_size = df.shape[0]
        logger.warning(
            "Removed {} rows with where the target variable is NA. Expected {} rows removed.".format(
                num_na, begin_size - end_size
            )
        )

    except KeyError:
        logger.warning(
            "Encountered error when attempting to drop columns and rows. Please double check columns to drop and target column are valid."
        )
        pass

    return df


def convert_variable_types(df):
    """Clean up variable types in the dataframe

    Args:
        df (:class:`pandas.DataFrame`): listings data

    Returns:
        :class:`pandas.DataFrame`: listings data with cleaned variable types
    """

    # Standardize zip codes as 5-digits
    try:
        df.loc[:, "zipcode"] = df["zipcode"].apply(
            lambda x: standardize_zipcode(str(x))
        )
        logger.info("Cleaned zipcode column.")
    except Exception as e:
        logger.warning("Encountered error when attempting to clean zipcode column.")
        logger.error(e)
        pass

    # Define price columns
    price_cols = [
        "price",
        "weekly_price",
        "monthly_price",
        "security_deposit",
        "cleaning_fee",
        "extra_people",
    ]

    for col in price_cols:
        # Remove the dollar sign and set price columns to numeric data types
        try:
            df.loc[:, col] = df[col].apply(lambda x: convert_price(str(x)))
            logger.info("Cleaned {} column.".format(col))
        except Exception as e:
            logger.warning(
                "Encountered error when attempting to clean {} column.".format(col)
            )
            logger.error(e)
            continue

    # Remove the percentage sign and convert host_response_rate to numeric
    try:
        df.loc[:, "host_response_rate"] = df["host_response_rate"].apply(
            lambda x: convert_percentage(str(x))
        )
        logger.info("Cleaned host_response_rate column.")
    except Exception as e:
        logger.warning(
            "Encountered error when attempting to clean host_response_rate column."
        )
        logger.error(e)
        pass

    return df


def standardize_zipcode(zip):
    """Return 5 digit zip code"""

    try:
        return zip[0:5]
    except Exception as e:
        logger.error("Encountered error when trying to parse zip code.")
        logger.error(e)


def convert_price(price):
    """Return numeric value for price"""

    if price[0] == "$":
        price = price[1:]

    if price.find(",") != -1:
        price = price.replace(",", "")

    try:
        return round(float(price), 2)
    except Exception as e:
        logger.error("Encountered error when trying to convert price.")
        logger.error(e)


def convert_percentage(pct):
    """Return numeric decimal value for percentage"""

    if pct[-1] == "%":
        pct = pct[:-1]

    try:
        return round(float(pct) / 100, 2)
    except Exception as e:
        logger.error("Encountered error when trying to convert percentage.")
        logger.error(e)
