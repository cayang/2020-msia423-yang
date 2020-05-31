import os
import argparse
import logging
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
import yaml

Base = declarative_base()


class Listings(Base):
    """Create a data model for the database to be set up for capturing listing data"""

    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    host_since_years = Column(Numeric, unique=False, nullable=True)
    host_response_time = Column(String(100), unique=False, nullable=True)
    host_response_rate = Column(String(100), unique=False, nullable=True)
    host_is_superhost = Column(Boolean, unique=False, nullable=True)
    host_listings_count = Column(Integer, unique=False, nullable=True)
    host_has_profile_pic = Column(Boolean, unique=False, nullable=True)
    host_has_identity_verified = Column(Boolean, unique=False, nullable=True)
    is_location_exact = Column(Boolean, unique=False, nullable=True)
    property_type_cat = Column(String(100), unique=False, nullable=True)
    room_type = Column(String(100), unique=False, nullable=True)
    accommodates_cat = Column(Integer, unique=False, nullable=True)
    bathrooms_cat = Column(Integer, unique=False, nullable=True)
    beds_cat = Column(Integer, unique=False, nullable=True)
    bed_type_cat = Column(String(100), unique=False, nullable=True)
    amenities_count = Column(Integer, unique=False, nullable=True)
    price = Column(Numeric, unique=False, nullable=True)
    security_deposit = Column(Numeric, unique=False, nullable=True)
    cleaning_fee = Column(Numeric, unique=False, nullable=True)
    guests_included_cat = Column(Integer, unique=False, nullable=True)
    extra_people_cat = Column(Integer, unique=False, nullable=True)
    neighbourhood_group = Column(String(100), unique=False, nullable=True)
    min_nights_cat = Column(Integer, unique=False, nullable=True)
    max_nights_cat = Column(Integer, unique=False, nullable=True)
    instant_bookable = Column(Boolean, unique=False, nullable=True)
    cancellation_policy = Column(String(100), unique=False, nullable=True)
    require_guest_profile_picture = Column(Boolean, unique=False, nullable=True)
    require_guest_phone_verificataion = Column(Boolean, unique=False, nullable=True)

    def __repr__(self):
        return "<Listings %r>" % self.id


def run_create_db(args):
    """Creates a SQLAlchemy session and database schema

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - local: specification of whether to create local SQLite table RDS table
    """

    if args.local == True:
        engine_string = "sqlite:////{}".format(args.config.DATABASE_PATH)
    else:
        user = os.environ.get("MYSQL_USER")
        password = os.environ.get("MYSQL_PASSWORD")
        host = os.environ.get("MYSQL_HOST")
        port = os.environ.get("MYSQL_PORT")

        engine_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(
            user, password, host, port, args.config.RDS_DATABASE
        )

    create_db(engine_string)


def create_db(engine_string):
    """Creates a database with the data models inherited from `Base` (Listings).

    Args:
        engine_string (`str`, default None): String defining SQLAlchemy connection URI
    """

    # Set up MySQL connection
    engine = sql.create_engine(engine_string)

    # Create Listings database
    Base.metadata.create_all(engine)

    # Create db session to persist
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add records
    # NOTE: This might go into a different module to separate creating the database
    # schema vs. uploading data into the table
    persist_records(session, engine)


# TODO: Write function to persist listings data to database - might go into
# a different module
def persist_records(session, engine):
    pass
