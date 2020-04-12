# Increasing Engagement in the Chicago Homestays Marketplace
Developer: Catherine Yang  
QA support: Thomas Kuo

## Project Charter

### Background

 With the rise of the sharing economy, homestays have become an increasingly popular lodging option for short-term stays and short-term rentals. [Airbnb] (https://www.airbnb.com/) is a platform that provides an online marketplace for hosts to list their accommodations and for guests to book such homestays. Encouraging growth in the homestays marketplace benefits both guests, who can seek a wider variety of alternative options for lodging, as well as hosts, who can earn income through renting out their listings.

### Vision

To increase user engagement on the Airbnb platform (users referring to both hosts and guests), and to grow the homestays market in the Chicago area, particularly on the Airbnb platform.

### Mission

To provide the tools and infrastructure that would help:
- Understand the features driving the number reviews per month (used as a proxy for measuring booking activity and overall user engagement) for a particular listing. 
- Predict the number of reviews per month a listing will receive, based on features pertaining to its host, accommodation, and booking process. A variety of regression models will be tried and evaluated for predictive performance in order to select the most optimal model.

This serves a twofold purpose for guests and hosts. For guests, more reviews would generate greater user interaction with the platform and can inform future prospective guests' boooking decisions. This will lead to the acquisition of new users and increase bookings within existing user base. For hosts, providing insight into attributes driving increased reviews (and bookings) will help lead to growth in the number of hosts and listings on the Airbnb platform, as well as help optimize hospitality for existing listings.

Data source: [Airbnb listing-level data] (http://insideairbnb.com/get-the-data.html) for the Chicago area (updated every month)

### Success Criteria

1. **Model Performance Metric**: 
    - MSE - Desired MSE prior to model deployment: ***< 0.25*** (i.e., we want the predicted reviews per month should be within 0.5 of the actual reviews per month, on average across all listings, in order to provide prospective hosts with an reasonably accurate assessment). 

2. **Business Metrics**:
    - % Increase in average reviews per month per listing, across all listings, month over month
    - % Increase in total listings, month over month
    - % Increase in number of unique hosts, month over month

### Plan

#### Initiative 1: Develop Underlying Model and Web-app Infrastructure (Solution Prototype)
- **Epic 1**: Develop Initial Predictive Model (Train Model Object)
  - Story 1: Obtain, clean, and prepare dataset in format required for model ingestion - PLANNED
  - Story 2: Asses dataset features, perform transformations as needed, and select features for predictive model - PLANNED
  - Story 3: Build predictive model(s) - linear & penalized regressions (Lasso, Elastic Net), random forest, boosted tree, neural network - and compare predictive performance to select best model type - PLANNED
  - Story 4: Tune best model type to obtain trained model object - PLANNED
- **Epic 2**: Develop Webapp Infrastructure
  - Story 1: Develop front-end input and features - PLANNED
  - Story 2: Integrate model output with Flask application - PLANNED
- **Epic 3**: Refine Predictive Model by Testing New Features and Feature Selection Methodologies
  - Story 1: (Specific tasks to be further defined at a later time) - ICEBOX
- **Epic 4**: Refine Predictive Model by Testing Different Model Types
  - Story 1: (Specific tasks to be further defined at a later time) - ICEBOX
- **Epic 5**: Refine Flask application interface for more optimal user experience
  - Story 1: (Specific tasks to be further defined at a later time) - ICEBOX

#### Initiative 2: Develop Data Infrastructure for Web-app Deployment
- **Epic 1**: Build Data Acquisition Pipeline
  - Story 1: Develop scripts that ingest data from source and produce raw data files - PLANNED
  - Story 2: Develop scripts that create local database schema - PLANNED
  - Story 3: Integrate data pipeline with feature pipeline and model training process - PLANNED
  - Story 4: Conduct appropriate tests to ensure performance is as expected - PLANNED
- **Epic 2**: Optimize Data Pipeline with Alternative Acquisition and Storage
  - Story 1: (Specific tasks to be further defined at a later time) - ICEBOX

### Backlog

- Initiative1.epic1.story1 (small) - PLANNED
- Initiative1.epic1.story2 (medium) - PLANNED
- Initiative1.epic1.story3 (big) - PLANNED
- Initiative1.epic1.story4 (medium) - PLANNED
- Initiative1.epic2.story1 (medium) - PLANNED
- Initiative1.epic2.story2 (large) - PLANNED
- Initiative2.epic1.story1 (large) - PLANNED
- Initiative2.epic1.story2 (medium) - PLANNED
- Initiative2.epic1.story3 (medium) - PLANNED
- Initiative2.epic1.story4 (medium) - PLANNED
 
Sizing: small < medium < large < big

### Icebox
- Initiative1.epic3 
- Initiative1.epic4
- Initiative1.epic5
- Initiative2.epic2

---

## Project Repository

<!-- toc -->

- [Directory structure](#directory-structure)
- [Running the app](#running-the-app)
  * [1. Initialize the database](#1-initialize-the-database)
    + [Create the database with a single song](#create-the-database-with-a-single-song)
    + [Adding additional songs](#adding-additional-songs)
    + [Defining your engine string](#defining-your-engine-string)
      - [Local SQLite database](#local-sqlite-database)
  * [2. Configure Flask app](#2-configure-flask-app)
  * [3. Run the Flask app](#3-run-the-flask-app)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Build the image](#1-build-the-image)
  * [2. Run the container](#2-run-the-container)
  * [3. Kill the container](#3-kill-the-container)

<!-- tocstop -->

## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the app
### 1. Initialize the database 

#### Create the database with a single song 
To create the database in the location configured in `config.py` with one initial song, run: 

`python run.py create_db --engine_string=<engine_string> --artist=<ARTIST> --title=<TITLE> --album=<ALBUM>`

By default, `python run.py create_db` creates a database at `sqlite:///data/tracks.db` with the initial song *Radar* by Britney spears. 
#### Adding additional songs 
To add an additional song:

`python run.py ingest --engine_string=<engine_string> --artist=<ARTIST> --title=<TITLE> --album=<ALBUM>`

By default, `python run.py ingest` adds *Minor Cause* by Emancipator to the SQLite database located in `sqlite:///data/tracks.db`.

#### Defining your engine string 
A SQLAlchemy database connection is defined by a string with the following format:

`dialect+driver://username:password@host:port/database`

The `+dialect` is optional and if not provided, a default is used. For a more detailed description of what `dialect` and `driver` are and how a connection is made, you can see the documentation [here](https://docs.sqlalchemy.org/en/13/core/engines.html). We will cover SQLAlchemy and connection strings in the SQLAlchemy lab session on 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

```python
engine_string='sqlite:///data/tracks.db'

```

The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).

You can also define the absolute path with four `////`, for example:

```python
engine_string = 'sqlite://///Users/cmawer/Repos/2020-MSIA423-template-repository/data/tracks.db'
```


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

To run the Flask app, run: 

```bash
python app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

## Running the app in Docker 

### 1. Build the image 

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f app/Dockerfile -t pennylane .
```

This command builds the Docker image, with the tag `pennylane`, based on the instructions in `app/Dockerfile` and the files existing in this directory.
 
### 2. Run the container 

To run the app, run from this directory: 

```bash
docker run -p 5000:5000 --name test pennylane
```
You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

This command runs the `pennylane` image as a container named `test` and forwards the port 5000 from container to your laptop so that you can access the flask app exposed through that port. 

If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `app/Dockerfile`)

### 3. Kill the container 

Once finished with the app, you will need to kill the container. To do so: 

```bash
docker kill test 
```

where `test` is the name given in the `docker run` command.