# IMPORTS
import pandas as pd
import numpy as np
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Dictionary of
LISTING_DTYPES = {
    "zipcode": "str",
    "price": "str",
    "weekly_price": "str",
    "monthly_price": "str",
    "security_deposit": "str",
    "cleaning_fee": "str",
}

DROP_COLS = [
    "listing_url",
    "scrape_id",
    "last_scraped",
    "experiences_offered",
    "thumbnail_url",
    "medium_url",
    "picture_url",
    "xl_picture_url",
    "host_thumbnail_url",
    "host_picture_url",
    "smart_location",
    "calendar_last_scraped",
    "license",
    "require_guest_profile_picture",
    "require_guest_phone_verification",
    "host_url",
    "requires_license",
    "has_availability",
    "jurisdiction_names",
    "neighbourhood",
]


def get_cleaned_data(data_file_listings):
    """Imports raw data file, cleans data formats, and removes unused columns
    
    Args:
        data_file_listings (str): filepath of the raw listing data in CSV format
    
    Returns:
        df_listings (DataFrame): cleaned listing dataset
    """

    # Read in data
    df_listings = pd.read_csv(
        data_file_listings, na_values=["NaN", "N/A"], dtype=LISTING_DTYPES
    )

    # Standardize zip codes as 5-digits
    df_listings.loc[:, "zipcode"] = df_listings["zipcode"].str[0:5]

    # Set prices to numeric data types
    df_listings.loc[:, "price"] = (
        df_listings["price"].str.replace(",", "").str[1:].astype(float)
    )
    df_listings.loc[:, "weekly_price"] = (
        df_listings["weekly_price"].str.replace(",", "").str[1:].astype(float)
    )
    df_listings.loc[:, "monthly_price"] = (
        df_listings["monthly_price"].str.replace(",", "").str[1:].astype(float)
    )
    df_listings.loc[:, "security_deposit"] = (
        df_listings["security_deposit"].str.replace(",", "").str[1:].astype(float)
    )
    df_listings.loc[:, "cleaning_fee"] = (
        df_listings["cleaning_fee"].str.replace(",", "").str[1:].astype(float)
    )
    df_listings.loc[:, "extra_people"] = (
        df_listings["extra_people"].str.replace(",", "").str[1:].astype(float)
    )

    # Drop unused columns
    df_listings = df_listings.drop(columns=DROP_COLS, axis=1)

    return df_listings
