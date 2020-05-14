# IMPORTS
import sys
import pathlib
import argparse
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
import yaml

from config import YAML_CONFIG, DATA_FILENAME_CLEAN, DATA_FILENAME_FEATURES, PULL_DATE

# Options
pd.options.mode.chained_assignment = None


def run_generate_features(args):
    """Generate all features and select features that will be used for model training

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - select_features: specification of whether to use manually selected features listed in the modelconfig.yml file
    """

    # Load in configs from yml file
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        FEATURES_HOST = config["generate_features"]["FEATURES_HOST"]
        FEATURES_PROP = config["generate_features"]["FEATURES_PROP"]
        FEATURES_BOOKING = config["generate_features"]["FEATURES_BOOKING"]
        SELECT_FEATURES = config["generate_features"]["SELECT_FEATURES"]

    # Read in the clean data with entire feature set
    df = pd.read_csv(DATA_FILENAME_CLEAN)

    # Create features
    df = create_host_features(df)
    df = create_property_features(df)
    df = create_booking_features(df)

    # Get columns of final dataframe
    if args.select_features == True:
        df = df[SELECT_FEATURES + ["reviews_per_month"]]

    else:
        df = df[
            FEATURES_HOST + FEATURES_PROP + FEATURES_BOOKING + ["reviews_per_month"]
        ]

    # Export features and target variable to CSV
    df.to_csv(DATA_FILENAME_FEATURES, index=False)


def create_host_features(df):
    """Perform transformations on listings dataframe to create host features"""

    # Convert host_since to datetime
    df.loc[:, "host_since"] = pd.to_datetime(df["host_since"])

    # Add a feature for number of years as host
    df.loc[:, "host_since_years"] = round(
        (PULL_DATE - df["host_since"]) / np.timedelta64(1, "Y"), 2
    )

    # Convert host_is_superhost to 0/1
    df.loc[df["host_is_superhost"] == "t", "host_is_superhost"] = 1
    df.loc[df["host_is_superhost"] == "f", "host_is_superhost"] = 0

    # Convert host_has_profile_pic to 0/1
    df.loc[df["host_has_profile_pic"] == "t", "host_has_profile_pic"] = 1
    df.loc[df["host_has_profile_pic"] == "f", "host_has_profile_pic"] = 0

    # Convert host_identity_verified to 0/1
    df.loc[df["host_identity_verified"] == "t", "host_identity_verified"] = 1
    df.loc[df["host_identity_verified"] == "f", "host_identity_verified"] = 0

    return df


def create_property_features(df):
    """Perform transformations on listings dataframe to create property features"""

    # Convert is_location_exact to 0/1
    df.loc[df["is_location_exact"] == "t", "is_location_exact"] = 1
    df.loc[df["is_location_exact"] == "f", "is_location_exact"] = 0

    # Create new variable to categorize property_type
    # NOTE: Property categories are arbitrary. Categorization to be revisited
    df.loc[:, "property_type_cat"] = df["property_type"]
    df.loc[
        ~df["property_type"].isin(["Apartment", "House", "Condominium"]),
        "property_type_cat",
    ] = "Other"

    # Create new variable to categorize accommodates
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

    # Create new variable to categorize bedrooms
    df.loc[:, "bedrooms_cat"] = df["bedrooms"]
    df.loc[df["bedrooms"].isna(), "bedrooms_cat"] = np.minimum(df["beds"], 3)
    df.loc[df["bedrooms"] >= 3, "bedrooms_cat"] = 3

    # Create new variable to categorize bathrooms
    df.loc[:, "bathrooms_cat"] = df["bathrooms"]
    df.loc[df["bathrooms"].isna(), "bathrooms_cat"] = df["bedrooms"]
    df.loc[df["bathrooms"] < 2, "bathrooms_cat"] = 1
    df.loc[(df["bathrooms"] >= 2) & (df["bathrooms"] < 3), "bathrooms_cat",] = 2
    df.loc[df["bathrooms"] >= 3, "bathrooms_cat"] = 3

    # Create new variable to categorize beds
    df.loc[:, "beds_cat"] = df["beds"]

    # For listings where # beds = 0, assume that there is 1 bed per bedroom.
    # If # bedrooms = 0, set as 1
    df.loc[(df["beds"] == 0) | (df["beds"].isna()), "beds_cat"] = np.minimum(
        np.maximum(df["bedrooms"], 1), 5
    )
    df.loc[df["beds"] >= 5, "beds_cat"] = 5

    # Create new variable to categorize bed_type
    df.loc[:, "bed_type_cat"] = df["bed_type"]
    df.loc[~df["bed_type"].isin(["Real Bed"]), "bed_type_cat"] = "Other"

    # Create new variable to categorize guests_included
    df.loc[:, "guests_included_cat"] = df["guests_included"]
    df.loc[df["guests_included"] > 2, "guests_included_cat"] = 3

    # Create new variable to categorize extra_people
    df.loc[:, "extra_people_cat"] = df["extra_people"]
    df.loc[df["extra_people"] > 0, "extra_people_cat"] = 1

    # Create variable as count of # of amenities
    df.loc[:, "amenities_count"] = df["amenities"].str[1:-1].str.split(",").str.len()

    # Convert require_guest_profile_picture to 0/1
    df.loc[
        df["require_guest_profile_picture"] == "t", "require_guest_profile_picture"
    ] = 1
    df.loc[
        df["require_guest_profile_picture"] == "f", "require_guest_profile_picture"
    ] = 0

    # Convert require_guest_phone_verification to 0/1
    df.loc[
        df["require_guest_phone_verification"] == "t",
        "require_guest_phone_verification",
    ] = 1
    df.loc[
        df["require_guest_phone_verification"] == "f",
        "require_guest_phone_verification",
    ] = 0

    return df


def create_booking_features(df):
    """Perform transformations on listing data to create booking features"""

    # Convert instant_bookable to 0/1
    df.loc[df["instant_bookable"] == "t", "instant_bookable"] = 1
    df.loc[df["instant_bookable"] == "f", "instant_bookable"] = 0

    # Lump super_strict_30 and super_strict_60 with strict
    df.loc[
        (df["cancellation_policy"] == "super_strict_30")
        | (df["cancellation_policy"] == "super_strict_60"),
        "cancellation_policy",
    ] = "strict"

    # Create new variable to categorize minimum_nights
    df.loc[:, "min_nights_cat"] = df["minimum_nights"]
    df.loc[df["minimum_nights"] < 7, "min_nights_cat"] = 1
    df.loc[
        (df["minimum_nights"] >= 7) & (df["minimum_nights"] < 30), "min_nights_cat",
    ] = 2
    df.loc[df["minimum_nights"] >= 30, "min_nights_cat"] = 3

    # Create new variable to categorize maximum_nights
    df.loc[:, "max_nights_cat"] = df["maximum_nights"]
    df.loc[df["maximum_nights"] <= 30, "max_nights_cat"] = 1
    df.loc[
        (df["maximum_nights"] > 30) & (df["maximum_nights"] < 365), "max_nights_cat",
    ] = 2
    df.loc[df["maximum_nights"] >= 365, "max_nights_cat"] = 3

    return df


if __name__ == "__main__":

    # Add parsers for running generate_features
    parser = argparse.ArgumentParser(description="Run run_generate_features")
    subparsers = parser.add_subparsers()

    # Sub-parser
    sb_features = subparsers.add_parser(
        "features",
        description="Generates and selects a subset of features in prepration for training the model.",
    )
    sb_features.add_argument(
        "--config", default=YAML_CONFIG, help="Location of configuration YAML"
    )
    sb_features.add_argument(
        "--select_features",
        default=False,
        type=bool,
        help="Specifies whether to manually specify features to keep",
    )
    sb_features.set_defaults(func=run_generate_features)

    args = parser.parse_args()
    args.func(args)
