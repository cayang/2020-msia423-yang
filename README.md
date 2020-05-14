# Increasing Engagement in the Chicago Homestays Marketplace
Developer: Catherine Yang  
QA support: Thomas Kuo

## Project Charter

### Background

 With the rise of the sharing economy, homestays have become an increasingly popular lodging option for short-term stays and short-term rentals. [Airbnb](https://www.airbnb.com/) is a platform that provides an online marketplace for hosts to list their accommodations and for guests to book such homestays. Encouraging growth in the homestays marketplace benefits both guests, who can seek a wider variety of alternative options for lodging, as well as hosts, who can earn income through renting out their listings.

### Vision

To increase user engagement on the Airbnb platform (users referring to both hosts and guests), and to grow the homestays market in the Chicago area, particularly on the Airbnb platform.

### Mission

To provide the tools and infrastructure that would help:
- Understand the features driving the number reviews per month (used as a proxy for measuring booking activity and overall user engagement) for a particular listing. 
- Predict the number of reviews per month a listing will receive, based on features pertaining to its host, accommodation, and booking process. A variety of regression models will be tried and evaluated for predictive performance in order to select the most optimal model.

This serves a twofold purpose for guests and hosts. For guests, more reviews would generate greater user interaction with the platform and can inform future prospective guests' boooking decisions. This will lead to the acquisition of new users and increase bookings within existing user base. For hosts, providing insight into attributes driving increased reviews (and bookings) will help lead to growth in the number of hosts and listings on the Airbnb platform, as well as help optimize hospitality for existing listings.

Data source: [Airbnb listing-level data](http://insideairbnb.com/get-the-data.html) for the Chicago area (updated every month)

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
  - Story 1: Obtain, clean, and prepare dataset in format required for model ingestion - COMPLETE
  - Story 2: Asses dataset features, perform transformations as needed, and select features for predictive model - COMPLETE
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
  - Story 1: Develop scripts that ingest data from source and produce raw data files - COMPLETE
  - Story 2: Develop scripts that create local database schema - COMPLETE
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
- [Setup](#setup)
  * [1. Configure environment variables](#1-configure-environment-variables)
  * [2. Configure database (optional)](#2-configure-database-optional)
- [Running the Model Pipeline](#running-the-model-pipeline)
  * [1. Initialize the database](#1-initialize-the-database-schema)
  * [2. Ingest data from source and upload to S3 bucket](#2-ingest-data-from-source-and-upload-to-S3-bucket)
  * [3. Clean raw data](#3-clean-raw-data)
  * [4. Generate and select features](#4-generate-and-select-features)
- [Running the Model Pipeline in Docker (Optional)](#running-the-model-pipeline-in-docker-optional)
  * [1. Build the Docker image](#1-build-the-docker-image)
  * [2. Run model pipeline scripts](#2-run-model-pipeline-scripts)
- [Running MySQL in Command Line (Optional)](#running-mysql-in-command-line-optional)
  * [1. Configure MySQL environment variables](#1-configure-mysql-environment-variables)
  * [2. Run MySQL in Docker](#2-run-mysql-in-docker)

<!-- tocstop -->

## Directory structure 

```
├── README.md                         <- You are here
├── app
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── config.env                    <- Directory for keeping environment variables. **Do not sync** to Github. 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│   ├── modelconfig.yml               <- Configurations for S3 bucket, RDS DB name, and model pipeline components
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│   ├── neighbourhoods.csv            <- Static CSV file that contains map of neighborhoods to neighborhood groups
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
│   ├── clean_data.py                 <- Gets raw data from S3 bucket and cleans file.
│   ├── create_db.py                  <- Creates database schema (RDS or SQLite) and tables for data obtained after feature selection.
│   ├── generate_features.py          <- Creates and selects features from cleaned data in preparation for model training.
│   ├── ingest_data.py                <- Ingests data from source and uploads raw data to S3 bucket.
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── config.py                         <- Configurations for data source URL, and local filepath references (data files, databases) 
├── requirements.txt                  <- Python package dependencies 
```

## Setup

### 1. Configure environment variables

**Running locally**

Ensure AWS credentials are in the `~/.aws/credentials` file. 

Export MySQL credentials by running the following commands (replacing brackets <> with your own credentials):
```bash
export MYSQL_USER=<your-MySQL-user>
export MYSQL_PASSWORD=<your-MYSQL-password>
export MYSQL_HOST=<your-MySQL-host>
export MYSQL_PORT=<your-MySQL-port>
```

**Running in Docker**

Create a file called `config.env` file within the `config/` path. This file will contain your AWS credentials to access the S3 bucket, as well as your MySQL credentials for accessing the RDS table. The following environment variables will be exported to the Docker container when the scripts are executed:
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCESS_KEY_ID`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_HOST`
- `MYSQL_PORT`

To create the `config.env` file, from the root directory, run:
```bash
vi config/config.env
``` 
Copy the code below into the `config.env` file and replace the bracketed <> fields with your credentials):
```bash
# AWS credentials
AWS_SECRET_ACCESS_KEY=<your-AWS-secret-access-key>
AWS_ACCESS_KEY_ID=<your-AWS-access-key-id>

# MySQL credentials
MYSQL_USER=<your-MySQL-user>
MYSQL_PASSWORD=<your-MYSQL-password>
MYSQL_HOST=<your-MySQL-host>
MYSQL_PORT=<your-MySQL-port>
```

### 2. Configure database (optional)

**RDS**

To change the RDS database name, modify `RDS: DATABASE` in the `config/modelconfig.yml` file. Default database is:
```yml
RDS:
    DATABASE: airbnbchi_db
```

**Local SQLite**

To change the local filepath where the SQLite database is created, modify `DATABASE_PATH` variable in the `config.py` file. Default location is:
```python
DATABASE_PATH = HOME / "data" / "airbnbchi.db"
```
where `HOME` is the root directory. The `DATBASE_PATH` should be an **absolute path**, not a relative path.


## Running the Model Pipeline

All scripts should be executed by running `python run.py <arg>` in the root of the repository, where `<arg>` specifies the step in the model pipeline to execute. Details on the pipeline and arguments to pass are below.

### 1. Initialize the database schema

To create the database (default location is RDS), run:
```bash
python run.py create_db
```
To create the database locally, add argument `--local=True`
```bash
python run.py create_db --local=True
```

### 2. Ingest data from source and upload to S3 bucket

To import data from the source URL (source [here](http://insideairbnb.com/get-the-data.html)), run:
```bash
python run.py ingest
```

The S3 bucket location and object name can be configured by `S3: S3_BUCKET` and `S3: S3_OBJECT` in the `config/modelconfig.yml` file.

### 3. Clean raw data

To clean and pre-process the raw data file, run:
```bash
python run.py clean
```
The clean data CSV file will be saved locally in the `data/` folder. 

To delete the raw data file from the local folder, add `--keep_raw=False`
```bash
python run.py clean --keep_raw=False
```

### 4. Generate and select features

To generate and select features in preparation for model training, run:
```bash
python run.py features
```
A CSV file containing the selected features and target variable will be saved locally in the `data/` folder. This data will be loaded to the database.

## Running the Model Pipeline in Docker (Optional)

### 1. Build the Docker image

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run from this directory (the root of the repo): 
```bash
 docker build -f app/Dockerfile -t airbnbchi .
```
This command builds the Docker image, with the tag `airbnbchi`, based on the instructions in `app/Dockerfile` and the files existing in this directory.

### 2. Run model pipeline scripts

First, ensure that the `config.env` file is created in the `config/` path. Instructions for creating this file are referenced in the section [Configure environment variables](#1-configure-environment-variables).

To run the model pipeline scripts, run:
```bash
docker run --env-file=config/config.env airbnbchi run.py <pipeline_arg> --optional_args
```
The `pipeline_arg` is the argument that specifies which step of the pipeline to execute. For example, to create the database, run:
```bash
docker run --env-file=config/config.env airbnbchi run.py create_db
```
Refer to [Running the Model Pipeline](#running-the-model-pipeline) section for the arguments to pass in when executing the `run.py` script.

**Persisting data files and SQLite database locally**

To persist the data files and databases locally, include `--mount type=bind,source=$(pwd)/data,target=/app/data` in the `docker run` statement. 

For example, to save the SQLite database locally, run:
```bash
docker run --env-file=config/config.env --mount type=bind,source=$(pwd)/data,target=/app/data airbnbchi run.py create_db --local=True
```

## Running MySQL in Command Line (Optional)

Once the RDS table has been created, you can access the database via MySQL in the command line. 

### 1. Configure MySQL environment variables

First, configure environment variables by either:

1. Exporting the variables directly in the command line by running the following commands:
    ```bash
    export MYSQL_USER=<your-MySQL-user>
    export MYSQL_PASSWORD=<your-MYSQL-password>
    export MYSQL_HOST=<your-MySQL-host>
    export MYSQL_PORT=<your-MySQL-port>
    ```

2.  Creating a `.mysqlconfig` file via command `vi .mysqlconfig` in the root of the repository to store the code above:

    ```bash
    export MYSQL_USER=<your-MySQL-user>
    export MYSQL_PASSWORD=<your-MYSQL-password>
    export MYSQL_HOST=<your-MySQL-host>
    export MYSQL_PORT=<your-MySQL-port>
    ```
    Then, run the following in command line to export the environment variables:
    ```bash
    echo 'source .mysqlconfig' >> ~/.bashrc
    source ~/.bashrc
    ```

### 2. Run MySQL in Docker

Access the RDS table via MySQL in command line by executing the following:
```bash
docker run -it --rm mysql:latest mysql -h${MYSQL_HOST} -u${MYSQL_USER} -p${MYSQL_PASSWORD}
```


