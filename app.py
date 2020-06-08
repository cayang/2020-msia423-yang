import traceback
from flask import render_template, request, redirect, url_for
import logging.config
import pandas as pd
import numpy as np

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import config
from src.predict import run_predict
from src.create_db import Listings


# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Configure flask app from flask_config.py
app.config.from_pyfile("config.py")

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug("Test log")

# Initialize the database
db = SQLAlchemy(app)


@app.route("/")
def index():
    """Main view that lists the app's web page.

    Create view into index page that servers as the platform to input data in order to
    generate a prediction.

    Returns: rendered html template
    """

    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add_entry():
    """View that process a POST with new listing input

    Returns: predicted number of reviews per month
    """

    # Create the input dataframe
    X = pd.DataFrame(
        {
            "host_since_years": float(request.form["host_since_years"]),
            "host_response_time": request.form["host_response_time"],
            "host_response_rate": float(request.form["host_response_rate"]),
            "host_is_superhost": int(request.form["host_is_superhost"]),
            "host_listings_count": int(request.form["host_listings_count"]),
            "host_has_profile_pic": int(request.form["host_has_profile_pic"]),
            "host_identity_verified": int(request.form["host_identity_verified"]),
            "is_location_exact": int(request.form["is_location_exact"]),
            "property_type_cat": request.form["property_type_cat"],
            "room_type": request.form["room_type"],
            "accommodates_cat": int(request.form["accommodates_cat"]),
            "bathrooms_cat": int(request.form["bathrooms_cat"]),
            "bedrooms_cat": int(request.form["bedrooms_cat"]),
            "beds_cat": int(request.form["beds_cat"]),
            "bed_type_cat": request.form["bed_type_cat"],
            "amenities_count": int(request.form["amenities_count"]),
            "price": float(request.form["price"]),
            "security_deposit": float(request.form["security_deposit"]),
            "cleaning_fee": float(request.form["cleaning_fee"]),
            "guests_included_cat": int(request.form["guests_included_cat"]),
            "extra_people_cat": int(request.form["extra_people_cat"]),
            "neighbourhood_group": request.form["neighbourhood_group"],
            "min_nights_cat": int(request.form["min_nights_cat"]),
            "max_nights_cat": int(request.form["max_nights_cat"]),
            "instant_bookable": int(request.form["instant_bookable"]),
            "cancellation_policy": request.form["cancellation_policy"],
            "require_guest_profile_picture": int(
                request.form["require_guest_profile_picture"]
            ),
            "require_guest_phone_verification": int(
                request.form["require_guest_phone_verification"]
            ),
        },
        index=np.arange(0, 1),
    )

    # Generate prediction result
    logger.info("Generating prediction.")
    try:
        result, perc = run_predict(X, modelconfig=config.YAML_CONFIG)
    except:
        logger.error("Unable to generate a prediction, error page returned.")
        return render_template("error.html", result="Result not available")

    # Write user input to database
    try:
        listing = Listings(
            host_since_years=float(request.form["host_since_years"]),
            host_response_time=request.form["host_response_time"],
            host_response_rate=float(request.form["host_response_rate"]),
            host_is_superhost=int(request.form["host_is_superhost"]),
            host_listings_count=int(request.form["host_listings_count"]),
            host_has_profile_pic=int(request.form["host_has_profile_pic"]),
            host_identity_verified=int(request.form["host_identity_verified"]),
            is_location_exact=int(request.form["is_location_exact"]),
            property_type_cat=request.form["property_type_cat"],
            room_type=request.form["room_type"],
            accommodates_cat=int(request.form["accommodates_cat"]),
            bathrooms_cat=int(request.form["bathrooms_cat"]),
            bedrooms_cat=int(request.form["bedrooms_cat"]),
            beds_cat=int(request.form["beds_cat"]),
            bed_type_cat=request.form["bed_type_cat"],
            amenities_count=int(request.form["amenities_count"]),
            price=float(request.form["price"]),
            security_deposit=float(request.form["security_deposit"]),
            cleaning_fee=float(request.form["cleaning_fee"]),
            guests_included_cat=int(request.form["guests_included_cat"]),
            extra_people_cat=int(request.form["extra_people_cat"]),
            neighbourhood_group=request.form["neighbourhood_group"],
            min_nights_cat=int(request.form["min_nights_cat"]),
            max_nights_cat=int(request.form["max_nights_cat"]),
            instant_bookable=int(request.form["instant_bookable"]),
            cancellation_policy=request.form["cancellation_policy"],
            require_guest_profile_picture=int(
                request.form["require_guest_profile_picture"]
            ),
            require_guest_phone_verification=int(
                request.form["require_guest_phone_verification"]
            ),
            reviews_per_month=result,
        )
        db.session.add(listing)
        db.session.commit()
        logger.info("New listing added.")

        # Query table results and expose info from last few user queries
        query = db.session.query(Listings).limit(app.config["MAX_ROWS_SHOW"]).all()

        return render_template(
            "index.html", inputs=query, result=result, percentile=perc, scroll="result"
        )

    except:
        traceback.print_exc()
        logger.warning("Not able to display prediction, error page returned")
        return render_template("error.html", result="Result not available")


if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])
