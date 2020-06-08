import os
import logging
import logging.config
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean
import yaml

import config

logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Listings(Base):
    """Create a data model for the database to be set up for capturing listing data"""

    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    host_since_years = Column(Numeric, unique=False, nullable=True)
    host_response_time = Column(String(100), unique=False, nullable=True)
    host_response_rate = Column(Numeric, unique=False, nullable=True)
    host_is_superhost = Column(Boolean, unique=False, nullable=True)
    host_listings_count = Column(Integer, unique=False, nullable=True)
    host_has_profile_pic = Column(Boolean, unique=False, nullable=True)
    host_identity_verified = Column(Boolean, unique=False, nullable=True)
    is_location_exact = Column(Boolean, unique=False, nullable=True)
    property_type_cat = Column(String(100), unique=False, nullable=True)
    room_type = Column(String(100), unique=False, nullable=True)
    accommodates_cat = Column(Integer, unique=False, nullable=True)
    bathrooms_cat = Column(Integer, unique=False, nullable=True)
    bedrooms_cat = Column(Integer, unique=False, nullable=True)
    beds_cat = Column(Integer, unique=False, nullable=True)
    bed_type_cat = Column(String(100), unique=False, nullable=True)
    amenities_count = Column(Integer, unique=False, nullable=True)
    price = Column(Numeric, unique=False, nullable=True)
    security_deposit = Column(Numeric, unique=False, nullable=True)
    cleaning_fee = Column(Numeric, unique=False, nullable=True)
    guests_included_cat = Column(Integer, unique=False, nullable=True)
    extra_people_cat = Column(Boolean, unique=False, nullable=True)
    neighbourhood_group = Column(String(100), unique=False, nullable=True)
    min_nights_cat = Column(Integer, unique=False, nullable=True)
    max_nights_cat = Column(Integer, unique=False, nullable=True)
    instant_bookable = Column(Boolean, unique=False, nullable=True)
    cancellation_policy = Column(String(100), unique=False, nullable=True)
    require_guest_profile_picture = Column(Boolean, unique=False, nullable=True)
    require_guest_phone_verification = Column(Boolean, unique=False, nullable=True)
    reviews_per_month = Column(Numeric, unique=False, nullable=True)

    def __repr__(self):
        return "<Listings %r>" % self.id


def run_create_db(args):
    """Creates a SQLAlchemy session and database schema

    Args:
        args (args from user): contains
            - config: location of YAML config file
            - truncate: specification of whether to remove existing table
            - engine_string: engine string for creating database
    """

    if args.truncate:
        try:
            logger.info("Attempting to truncate listings table.")
            _truncate_listings(args.engine_string)
            logger.info("listings table truncated.")
        except Exception as e:
            logger.error("Error occurred while attempting to truncate listings table.")
            logger.error(e)
            pass

    if args.engine_string is None:
        return ValueError("`engine` or `engine_string` must be provided.")
    else:
        logger.info(
            "Connecting to database with engine string {}.".format(args.engine_string)
        )
        create_db(args.engine_string)


def create_db(engine_string):
    """Creates a database with the data models inherited from `Base` (Listings).

    Args:
        engine_string (`str`, default None): String defining SQLAlchemy connection URI
    """

    # Set up SQL connection
    engine = sql.create_engine(engine_string)

    # Create Listings database
    Base.metadata.create_all(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    session.commit()
    session.close()


def _truncate_listings(engine_string):
    """Deletes listings table if rerunning and run into unique key error."""

    # Set up MySQL connection
    engine = sql.create_engine(engine_string)

    # Create db session to persist
    Session = sessionmaker(bind=engine)
    session = Session()

    session.execute("""DELETE FROM listings""")
    session.commit()
    session.close()
