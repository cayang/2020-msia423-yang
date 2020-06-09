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

This serves a twofold purpose for guests and hosts. For guests, more reviews would generate greater user interaction with the platform and can inform future prospective guests' booking decisions. This will lead to the acquisition of new users and increase bookings within existing user base. For hosts, providing insight into attributes driving increased reviews (and bookings) will help lead to growth in the number of hosts and listings on the Airbnb platform, as well as help optimize hospitality for existing listings.

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
  - Story 3: Build predictive model(s) - linear & penalized regressions (Lasso, Elastic Net), random forest, boosted tree, neural network - and compare predictive performance to select best model type - COMPLETE
  - Story 4: Tune best model type to obtain trained model object - COMPLETE
- **Epic 2**: Develop Webapp Infrastructure
  - Story 1: Develop front-end input and features - COMPLETE
  - Story 2: Integrate model output with Flask application - COMPLETE
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
  - Story 3: Integrate data pipeline with feature pipeline and model training process - COMPLETE
  - Story 4: Conduct appropriate tests to ensure performance is as expected - COMPLETE
- **Epic 2**: Optimize Data Pipeline with Alternative Acquisition and Storage
  - Story 1: (Specific tasks to be further defined at a later time) - ICEBOX

### Backlog

- Initiative1.epic1.story1 (small) - COMPLETE
- Initiative1.epic1.story2 (medium) - COMPLETE
- Initiative1.epic1.story3 (big) - COMPLETE
- Initiative1.epic1.story4 (medium) - COMPLETE
- Initiative1.epic2.story1 (medium) - COMPLETE
- Initiative1.epic2.story2 (large) - COMPLETE
- Initiative2.epic1.story1 (large) - COMPLETE
- Initiative2.epic1.story2 (medium) - COMPLETE
- Initiative2.epic1.story3 (medium) - COMPLETE
- Initiative2.epic1.story4 (medium) - COMPLETE
 
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
- [Running the Model Pipeline](#running-the-model-pipeline)
- [Running the Flask App](#running-the-flask-app)
- [Running Unit Tests](#running-unit-tests)
- [Addendum: Configurations](#addendum-configurations)
  * [1. Configure environment variables](#1-configure-environment-variables)
  * [2. Configure database connection string](#2-configure-database-connection-string)
  * [3. Configure S3 bucket](#3-configure-s3-bucket)
- [Addendum: Running Model Pipeline Individual Steps](#addendum-running-model-pipeline-individual-steps)
  * [1. Ingest data from source and upload to S3 bucket](#1-ingest-data-from-source-and-upload-to-S3-bucket)
  * [2. Clean raw data](#2-clean-raw-data)
  * [3. Generate and select features](#3-generate-and-select-features)
  * [4. Train model and create model artifacts](#4-train-model-and-create-model-artifacts)
- [Addendum: Running Model Pipeline Individual Steps in Docker](#running-model-pipeline-individual-steps-in-docker)
- [Addendum: Running Unit Test Individual Steps](#addendum-running-unit-test-individual-steps)
- [Addendum: Running Unit Test Individual Steps in Docker](#addendum-running-unit-test-individual-steps-in-Docker)
- [Addendum: Running MySQL in Command Line (Optional)](#addendum-running-mysql-in-command-line-optional)
  * [1. Configure MySQL environment variables](#1-configure-mysql-environment-variables)
  * [2. Run MySQL in Docker](#2-run-mysql-in-docker)

<!-- tocstop -->

## Directory structure 

```
├── README.md                         <- You are here
├── app
│   ├── static/                       <- CSS, JS files that remain static.
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs.
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile_app                <- Dockerfile for building image to run app.
│
├── config                            <- Directory for configuration files. 
│   ├── config.env                    <- Directory for keeping environment variables. **Do not sync** to Github. 
│   ├── logging/                      <- Configuration of python loggers.
│   ├── modelconfig.yml               <- Configurations for default relative file paths and model pipeline components.
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked. by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git.
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git.
│   ├── neighbourhoods.csv            <- Static CSV file that contains map of neighborhoods to neighborhood groups.
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder. 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc.
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries.
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state.
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project. 
│   ├── clean_data.py                 <- Gets raw data from S3 bucket and cleans file.
│   ├── create_db.py                  <- Creates database schema (RDS or SQLite) and tables for running the Flask webapp.
│   ├── generate_features.py          <- Creates and selects features from cleaned data in preparation for model training.
│   ├── helpers.py                    <- Helper functions used by multiple src scripts.
│   ├── ingest_data.py                <- Ingests data from source and uploads raw data to S3 bucket.
│   ├── predict.py                    <- Generates a predicted output value(s) given user input in the Flask webapp.
│   ├── train_model.py                    <- Creates the trained model object and artifacts used to drive prediction engine for the Flask webapp.
│
├── test/                             <- Files necessary for running model tests (see documentation below). 
│
├── app.py                            <- Flask wrapper for running the model. 
├── run.py                            <- Simplifies the execution of one or more of the src scripts.  
├── config.py                         <- Configurations for data source URL, SQL database engine strings, S3 bucket name, and Flask API.
├── requirements.txt                  <- Python package dependencies. 
├── Dockerfile                        <- Dockerfile for building the image to run model pipeline.
├── Makefile                          <- Makefile for running all steps in the model pipeline and for running all unit tests.  
```

## Running the Model Pipeline

Creates all artifacts needed to support the web application. 

Note: if the data has **not** already been ingested and uploaded to S3 (or saved locally), in the root of the repository, first run:

```bash
python run.py ingest
```

**Running locally**

In the root of the repository, run:

```bash
make all
```

**Running in Docker**

Step 1: Build Docker image

```bash
docker build -f Dockerfile -t airbnbchi .
```

Step 2: Produce all model pipeline artifacts

Note you will need to set your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` credentials in the following command line argument.

```bash
docker run -e AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key> -e AWS_ACCESS_KEY_ID=<your-aws-access-key-id> --mount type=bind,source=$(pwd),target=/app/ airbnbchi all
```

Alternatively, you can set the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` credentials in a `config.env` file in the `config/` directory.

```bash
docker run -env-file=config/config.env --mount type=bind,source=$(pwd),target=/app/ airbnbchi all
```

## Running the Flask App

**Running Locally**

Step 1: Initialize the database. In the root of the repository, run

```bash
python run.py create_db
```

Step 2: Run the app

```bash
python app.py
```

**Running in Docker**

Step 1: Build the Docker image

```bash
docker build -f app/Dockerfile_app -t airbnbchi .
```

Step 2: Run the app (includes initializing the database)

```bash
docker run -p 5000:5000 airbnbchi
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

**Notes on the Database**

- The database can be configured by specifying a connection string as the `SQLALCHEMY_DATABASE_URI` environment variable.
- By default, if `SQLALCHEMY_DATABASE_URI` is not provided as an environment variable, then if the `MYSQL_HOST` is provided as an environment variable, an RDS database is created (given that `MYSQL_USER` and `MYSQL_PASSWORD`, and `MYSQL_PORT` are also provided)
- If `MYSQL_HOST` is not provided as an environment variable, then a local SQLite database in the `/data` folder is created

## Running Unit Tests

**Running Locally**

In the *root* of the repository, run:

```bash
make tests_all
```

**Running in Docker**

Step 1: Build the Docker image (can use the same Docker image as the [model pipeline](#running-the-model-pipeline) if already built). If the Docker image for the model pipeline has already been built, you can skip this step.

```bash
docker build -f Dockerfile -t airbnbchi .
```

Step 2: Run the tests

```bash
docker run airbnbchi tests_all
```

You can create a `test` Docker container by specifying `--name test` after the `docker run` command.

----

## Addendum: Configurations

### 1. Configure environment variables

Two sets of environment variables are required to run the model pipeline and the web application using an RDS database:

1. AWS credentials for the model pipeline, to upload / download files from S3:
    - `AWS_SECRET_ACCESS_KEY`
    - `AWS_ACCESS_KEY_ID`
2. MySQL credentials for the web application, to store user data in an RDS database:
    - `MYSQL_USER`
    - `MYSQL_PASSWORD`
    - `MYSQL_HOST`
    - `MYSQL_PORT`
    - `MYSQL_DATABASE`  

If MySQL credentials are not exported as environment variables, the application will create a local SQLite database.

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

The environment variables can be exported in the `docker run` command via the `-e VAR=val` flag for each environment variable (see [Running Model Pipeline](#running-model-pipeline) in Docker).

Alternatively create a file called `config.env` file within the `config/` path to store the environment variables, which will be exported to the Docker container when the scripts are executed:

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
MYSQL_DATABASE=<your-MySQL-database-name>
```

Then, add `--env-file=config/config.env` after the applicable `docker run` statement to export the environment variables Docker.

### 2. Configure database connection string

**RDS Using MySQL**

The default database name is `airbnbchi_db`. This default can be modified in the `config.py` script:
```python
if DATABASE is None:
    DATABASE = "airbnbchi_db"  # Default RDS database
```

**Local SQLite**

To change the *default* local file path where the SQLite database is created, modify `DATABASE_PATH` variable in the `config.py` file. Default location is:
```python
DATABASE_PATH = HOME / "data" / "airbnbchi.db"
```
where `HOME` is the root of the directory. The `DATBASE_PATH` should be an **absolute path**, not a relative path.

### 3. Configure S3 bucket

To change the *default* S3 bucket for which files are uploaded and downloaded from, modify the `S3_BUCKET` variable in `config.py`. The S3 bucket specification can also be passed in as a command line argument (see [Ingest data from source and upload to S3 bucket](#1-ingest-data-from-source-and-upload-to-s3-bucket))

----

## Addendum: Running Model Pipeline Individual Steps

All scripts should be executed by running `python run.py <arg>` in the root of the repository, where `<arg>` specifies the step in the model pipeline to execute. Details on the pipeline and arguments to pass are below.

### 1. Ingest data from source and upload to S3 bucket

To import data from the source URL (source [here](http://insideairbnb.com/get-the-data.html)), run:
```bash
python run.py ingest
```
Optional argument flags / configurations:
- `--s3_bucket_name`: to specify the S3 bucket to upload raw data to

### 2. Clean raw data

To clean and pre-process the raw data file, run:
```bash
python run.py clean
```
The clean data CSV file will by default be saved locally in the `/data` folder. 

Optional argument flags / configurations
- `--s3_bucket_name`: to specify the S3 bucket to download raw data frome
- `--output`: to specify the file path + name where the cleaned data file will be output
- `--keep_raw=False` to delete the raw data file

### 3. Generate and select features

To generate and select features in preparation for model training, run:
```bash
python run.py features
```
A CSV file containing the selected features and target variable will by default be saved locally in the `/data` folder. 

Optional argument flags / configurations
- `--input`: to specify the file path + name of the cleaned data file
- `--output`: to specify the file path + name where the features file will be output

### 4. Train model and create model artifacts

To created the trained model objects, model artifacts (e.g., encoders, scalers), and results, run:
```bash
python run.py train
```
The trained model object, encoder, and scalers PKL files will by default be saved locally in the `models/` folder.

Optional argument flags / configurations
- `--input`: to specify the file path + name of the features CSV file
- `--output`: to specify the file path where the model artifacts are output. Must be a folder path and not file name.
- `--use_existing_params` (default True): to specify whether to use existing hyperparameter settings in the `config/modelconfig.yml` file or whether to tune hyperparameters via random grid search. Strongly suggest keeping this argument True, since tuning may take a while.
- `--upload` (default False): to specify whether to upload model artifacts to S3
- `--s3_bucket_name`: to specify the S3 bucket to upload model artifacts to, if `--upload=True`

## Addendum: Running Model Pipeline Individual Steps in Docker

### 1. Build the Docker image

```bash
 docker build -f Dockerfile -t airbnbchi .
```
This command builds the Docker image, with the tag `airbnbchi`, based on the instructions in `Dockerfile` and the files existing in this directory.

### 2. Run model pipeline scripts

Note: ensure data has first been ingested and uploaded to the S3 bucket.

To use the `config.env`, ensure that the `config.env` file is created in the `config/` path. Instructions for creating this file are referenced in the section [Configure environment variables](#1-configure-environment-variables).

The `docker run` commands for each step of the model pipeline are:

```bash
# Clean
docker run --env-file=config/config.env --mount type=bind,source=$(pwd)/data,target=/app/data airbnbchi data/listings-clean.csv

# Generate features
docker run --mount type=bind,source=$(pwd)/data,target=/app/data airbnbchi data/features.csv

# Train model
docker run --env-file=config/config.env --mount type=bind,source=$(pwd)/data,target=/app/models airbnbchi models
```

Note the --env-file flag is only needed for functions that require interaction with S3. Alternatively, instead of using an `.env` file, you can pass each environment variable in the `docker run` command. See [Configure environment variables](#1-configure-environment-variables)

Refer to [Addendum: Running Model Pipeline Individual Steps](#addendum-running-model-pipeline-individual-steps) section for the arguments to pass in when executing the `run.py` script.

The `--mount type=bind,source=$(pwd)/data,target=/app/data` is used to persist the files locally while running in Docker. 

----

## Addendum: Running Unit Test Individual Steps

All test scripts are located in the `/test` folder and should be executed by running `pytest test/<test_script.py>` in the root of the repository, where `<test_script.py>` specifies the unit test script execute.

Run the following commands to individually unit test each `src` script.

```bash
pytest test/test_ingest_data.py
pytest test/test_clean_data.py
pytest test/test_generate_features.py
pytest test/test_train_model.py
pytest test/test_predict.py
```

## Addendum: Running Unit Test Individual Steps in Docker

### 1. Build the Docker image

```bash
 docker build -f Dockerfile -t airbnbchi .
```
This command builds the Docker image, with the tag `airbnbchi`, based on the instructions in `Dockerfile` and the files existing in this directory.

### 2. Execute the test scripts

```bash
docker run airbnbchi test_ingest_data
docker run airbnbchi test_clean_data
docker run airbnbchi test_generate_features
docker run airbnbchi test_train_model
docker run airbnbchi test_predict
```

----

## Addendum: Running MySQL in Command Line (Optional)

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


