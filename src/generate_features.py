import sys
import pathlib
import pandas as pd
import numpy as np
import datetime
from datetime import date, datetime, timedelta
import logging
import logging.config
import yaml

import config

# Options
pd.options.mode.chained_assignment = None

logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def run_generate_features(args):
    """Generate all features and select features that will be used for model training

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - input: local file path of clean data file
            - output: local file path to output the features data
            - pull_date: as of date denoting version of the dataset pulled from source
    """

    logger.info("Reading in configs from modelconfig.yml.")
    try:
        # Load in configs from yml file
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            data_files = config["data_files"]
            TARGET_COL = config["TARGET_COL"]
            COLS_BOOL = config["generate_features"]["COLS_BOOL"]
            SELECT_FEATURES = config["generate_features"]["SELECT_FEATURES"]
    except KeyError:
        logger.error(
            "Encountered error when assigning variable from configurations file."
        )
        sys.exit(1)
    except (FileNotFoundError, IOError):
        logger.error("Encountered error in reading in the configurations file.")
        sys.exit(1)

    # Read in the clean data with entire feature set
    if args.input is None:
        logger.info(
            "Reading in cleaned data file {}.".format(data_files["DATA_FILENAME_CLEAN"])
        )
        df = pd.read_csv(data_files["DATA_FILENAME_CLEAN"])
    else:
        logger.info("Reading in cleaned data file {}.".format(args.input))
        df = pd.read_csv(args.input)

    # Convert pull date argument to datetime
    try:
        pull_date = datetime.strptime(args.pull_date, "%Y-%m-%d")
    except Exception as e:
        logger.warning(
            "Could not convert pull_date to datetime type. Setting pull_date to today."
        )
        logger.error(e)
        pull_date = datetime.today()
        pass

    # Create features
    logger.debug("Converting true/false columns to boolean type.")
    df = convert_truefalse(df, COLS_BOOL)
    logger.debug("Creating host features.")
    df = create_host_features(df, pull_date)
    logger.debug("Creating property features.")
    df = create_property_features(df)
    logger.debug("Creating booking features.")
    df = create_booking_features(df)

    # Check for missing features in the data from what those expected
    missing_features = [f for f in SELECT_FEATURES if f not in df.columns.tolist()]

    # If there are missing features, update `feature_columns` to only include the non-missing names.
    if len(missing_features) > 0:
        logger.warning(
            "Dataset is missing {} expected columns {}".format(
                len(missing_features), missing_features
            )
        )
        SELECT_FEATURES = [f for f in SELECT_FEATURES if f not in missing_features]

    # Get final feature columns and assemble final dataframe
    df = df[SELECT_FEATURES + [TARGET_COL]]
    logger.info(
        "Final dataframe to be exported contains {} features: {}.".format(
            len(SELECT_FEATURES), SELECT_FEATURES
        )
    )

    # Export features and target variable to CSV
    if args.output is None:
        df.to_csv(data_files["DATA_FILENAME_FEATURES"], index=False)
        logger.info(
            "Exported features data file to {}".format(
                data_files["DATA_FILENAME_FEATURES"]
            )
        )
    else:
        df.to_csv(args.output)
        logger.info("Exported features data file to {}".format(args.output))


def create_host_features(df, pull_date):
    """"Perform transformations on listings dataframe to create host features

    Args:
        df (:class:`pandas.DataFrame`): listings data
        pull_date (:class:`datetime.datetime`): reference date when file was posted

    Returns:
        :class:`pandas.DataFrame`: listings data with generated host features
    """

    try:
        # Convert host_since to datetime
        df.loc[:, "host_since"] = pd.to_datetime(df["host_since"])

        # Add a feature for number of years as host
        df.loc[:, "host_since_years"] = round(
            (pull_date - df["host_since"]) / np.timedelta64(1, "Y"), 2
        )
        logger.info("Created host_since_years feature.")
    except Exception:
        logger.warning("Could not create host_since_years feature.")
        pass

    return df


def create_property_features(df):
    """Perform transformations on listings dataframe to create property features"""

    # Create new variable to categorize property_type
    try:
        df.loc[:, "property_type_cat"] = df["property_type"]
        df.loc[
            ~df["property_type"].isin(["Apartment", "House", "Condominium"]),
            "property_type_cat",
        ] = "Other"
        logger.info("Created property_type_cat feature.")
    except Exception:
        logger.warning("Could not create property_type_cat feature.")
        pass

    # Create new variable to categorize accommodates
    try:
        df.loc[:, "accomodates_cat"] = df["accommodates"]
        df.loc[df["accommodates"] <= 2, "accommodates_cat"] = 1
        df.loc[
            (df["accommodates"] > 2) & (df["accommodates"] <= 4), "accommodates_cat",
        ] = 2
        df.loc[
            (df["accommodates"] > 4) & (df["accommodates"] <= 6), "accommodates_cat",
        ] = 3
        df.loc[
            (df["accommodates"] > 6) & (df["accommodates"] <= 8), "accommodates_cat",
        ] = 4
        df.loc[df["accommodates"] > 8, "accommodates_cat"] = 5
        logger.info("Created accommodates_cat feature.")
    except Exception:
        logger.warning("Could not create accommodates_cat feature.")
        pass

    # Create new variable to categorize bedrooms
    try:
        df.loc[:, "bedrooms_cat"] = df["bedrooms"]
        df.loc[df["bedrooms"].isna(), "bedrooms_cat"] = np.minimum(df["beds"], 3)
        df.loc[df["bedrooms"] >= 3, "bedrooms_cat"] = 3
        logger.info("Created bedrooms_cat feature.")
    except Exception:
        logger.warning("Could not create bedrooms_cat feature.")
        pass

    # Create new variable to categorize bathrooms
    try:
        df.loc[:, "bathrooms_cat"] = df["bathrooms"]
        df.loc[df["bathrooms"].isna(), "bathrooms_cat"] = df["bedrooms"]
        df.loc[df["bathrooms"] < 2, "bathrooms_cat"] = 1
        df.loc[(df["bathrooms"] >= 2) & (df["bathrooms"] < 3), "bathrooms_cat",] = 2
        df.loc[df["bathrooms"] >= 3, "bathrooms_cat"] = 3
        logger.info("Created bathrooms_cat feature.")
    except Exception:
        logger.warning("Could not create bathrooms_cat feature.")
        pass

    # Create new variable to categorize beds
    try:
        df.loc[:, "beds_cat"] = df["beds"]

        # For listings where # beds = 0, assume that there is 1 bed per bedroom.
        # If # bedrooms = 0, set as 1
        df.loc[(df["beds"] == 0) | (df["beds"].isna()), "beds_cat"] = np.minimum(
            np.maximum(df["bedrooms"], 1), 5
        )
        df.loc[df["beds"] >= 5, "beds_cat"] = 5
        logger.info("Created beds_cat feature.")
    except Exception:
        logger.warning("Could not create beds_cat feature.")
        pass

    # Create new variable to categorize bed_type
    try:
        df.loc[:, "bed_type_cat"] = df["bed_type"]
        df.loc[~df["bed_type"].isin(["Real Bed"]), "bed_type_cat"] = "Other"
        logger.info("Created bed_type_cat feature.")
    except Exception:
        logger.warning("Could not create bed_type_cat feature.")
        pass

    # Create new variable to categorize guests_included
    try:
        df.loc[:, "guests_included_cat"] = df["guests_included"]
        df.loc[df["guests_included"] > 2, "guests_included_cat"] = 3
        logger.info("Created guests_included_cat feature.")
    except Exception:
        logger.warning("Could not create guests_included_cat feature.")
        pass

    # Create new variable to categorize extra_people
    try:
        df.loc[:, "extra_people_cat"] = df["extra_people"]
        df.loc[df["extra_people"] > 0, "extra_people_cat"] = 1
        logger.info("Created extra_people_cat feature.")
    except Exception:
        logger.warning("Could not created extra_people_cat feature.")
        pass

    # Create variable as count of # of amenities
    try:
        df.loc[:, "amenities_count"] = (
            df["amenities"].str[1:-1].str.split(",").str.len()
        )
        logger.info("Created extra_people_cat feature.")
    except Exception:
        logger.warning("Could not create amenities_count feature.")
        pass

    return df


def create_booking_features(df):
    """Perform transformations on listing data to create booking features"""

    # Lump super_strict_30 and super_strict_60 with strict
    try:
        df.loc[
            (df["cancellation_policy"] == "super_strict_30")
            | (df["cancellation_policy"] == "super_strict_60"),
            "cancellation_policy",
        ] = "strict"
        logger.info("Created remapped cancellation_policy feature.")
    except Exception:
        logger.warning("Could not remap cancellation_policy feature.")
        pass

    # Create new variable to categorize minimum_nights
    try:
        df.loc[:, "min_nights_cat"] = df["minimum_nights"]
        df.loc[df["minimum_nights"] < 7, "min_nights_cat"] = 1
        df.loc[
            (df["minimum_nights"] >= 7) & (df["minimum_nights"] < 30), "min_nights_cat",
        ] = 2
        df.loc[df["minimum_nights"] >= 30, "min_nights_cat"] = 3
        logger.info("Created min_nights_cat feature.")
    except Exception:
        logger.warning("Could not create min_nights_cat feature.")
        pass

    # Create new variable to categorize maximum_nights
    try:
        df.loc[:, "max_nights_cat"] = df["maximum_nights"]
        df.loc[df["maximum_nights"] < 30, "max_nights_cat"] = 1
        df.loc[
            (df["maximum_nights"] >= 30) & (df["maximum_nights"] < 365),
            "max_nights_cat",
        ] = 2
        df.loc[df["maximum_nights"] >= 365, "max_nights_cat"] = 3
    except Exception:
        logger.warning("Could not create max_nights_cat feature.")
        pass

    return df


def convert_truefalse(df, cols):
    """Converts columns with t/f data values to 1/0 boolean type

    Args:
        df (:class:`pandas.DataFrame`): listings data
        cols (:obj:`list`): list of columns for which the boolean conversion applies to

    Returns:
        :class:`pandas.DataFrame`: listings data with true/false features converted to boolean type
    """

    for col in cols:
        try:
            df.loc[df[col] == "t", col] = 1
            df.loc[df[col] == "f", col] = 0
            logger.info("Converted {} column to boolean type.".format(col))
        except Exception:
            logger.warning("Could not convert {} to boolean type".format(col))
            continue

    return df
