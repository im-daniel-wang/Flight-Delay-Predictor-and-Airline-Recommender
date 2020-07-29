# MSiA423 Flight Delay Prediction

Name: Jue Wang  
QA: Xiaoling Zhang   

## Running the Model Pipeline
### 1. Configure AWS S3 Settings (__Optional__)
```buildoutcfg
vi src/config
```
These are the default S3 configurations. You can leave these configurations as is or change the path if you want. 

### 2. Build Docker Image
```buildoutcfg
docker build -t model .
```

### 3. Run the Model Pipeline
Export your AWS credentials via environment variables. 
```buildoutcfg
export AWS_ACCESS_KEY_ID=<your access key>
export AWS_SECRET_ACCESS_KEY=<your secret key>
```

You can configure the model parameters in __config/test.yaml__.
```buildoutcfg
vi config/test.yaml
```
```
train:
  train_model:
    test_size: 0.3
    target_col: delay
    max_depth: 10
```

Run the model pipeline. 
```buildoutcfg
docker run  --mount type=bind,source="$(pwd)/data",target=/app/data/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY model run_pipeline.sh
```

### 4. Run the Unit Tests
```buildoutcfg
docker run model run_unit_tests.sh
```

There are 10 unit tests in total for transform, train and predict located in src folder. 

## Running the App

The app will gather inputs from user and upload the inputs to the "flight" table in either RDS or sqlite. 

### 1. Build Docker Image
```buildoutcfg
docker build -f app/Dockerfile -t flights .
```

### 2. Run the Container
Set the environment variable ${SQLALCHEMY_DATABASE_URI} if you want to configure which mysql database to write records to. 

Since msia423instructor do not have CREATE and INSERT previlidge, I have created data/sqlite_flight.db to store user inputs locally.

If you don't set the environment variable, the program will default to writing to data/sqlite_flight.db.   

In the case where you have set the variable before but still want to store data locally, execute the following commands or __set the variable to blank__ to __make sure the url is valid__:
```buildoutcfg
export SQLALCHEMY_DATABASE_URI=sqlite:///data/sqlite_flight.db
```

Then, run the docker container. 
```buildoutcfg
docker run -e SQLALCHEMY_DATABASE_URI -p 5000:5000 -t -i --mount type=bind,source="$(pwd)/data",target=/app/data/ --name test flights
```
You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

### 3. Kill and Remove Docker Container
Open up a new terminal and enter the following commands:
```buildoutcfg
docker rm test
```





## Midpoint Instructions (Creating RDS/sqlite Table & Uploading data to S3)

### 1. Acquiring Data

The data has been downloaded legally from [Bureau of Transportation Statistics](https://www.transtats.bts.gov/DL_SelectFields.asp?Table_ID=236) which includes flight on-time performance data throughout 2019.  

Manually check variables that are of interests. For this project I've chosen the following variables: *YEAR, MONTH, DAY_OF_MONTH, DAY_OF_WEEK, OP_UNIQUE_CARRIER, ORIGIN, DEST, CRS_DEP_TIME, DEP_TIME, DEP_DELAY, CRS_ARR_TIME, ARR_TIME, ARR_DELAY, CRS_ELAPSED_TIME, ACTUAL_ELAPSED_TIME, AIR_TIME, DISTANCE*  

The randomly sampled subset of the data has been downloaded already and stored in data/external/sample.csv.  

### 2. Edit your MySQL credentials if you choose to later create and query from tables in RDS instance
```bash
vi .mysqlconfig
```

In ```.mysqlconfig```:  
```buildoutcfg
set 'MYSQL_USER' to your username when you created RDS instance
set 'MYSQL_PASSWORD' to your RDS password
set 'MYSQL_HOST' to your RDS endpoint url
set 'MYSQL_PORT' to 3306
set 'MYSQL_DATABASE' to name of the database
```

You can leave MYSQL_HOST, MYSQL_HOST, DATABASE_NAME as is. Then:
```buildoutcfg
source .mysqlconfig
```

### 3. Edit your AWS S3 bucket name for uploading data to S3
```buildoutcfg
vi src/config.py
```

In ```config.py```:
```buildoutcfg
set 'BUCKET_NAME' to your bucket name in S3
set 'S3_OBJECT_NAME' to your desired file name after it's uploaded in S3
```
You can leave other configurations as is. Remember to use quotes on strings. 

### 4. Build docker image called flight_db
```bash
docker build -t flight_db .
```

### 5. Upload data to S3
Substitute 'access key' and 's3 secret key' with your own credentials and run the following command:
```bash
docker run -e S3_PUBLIC_KEY=<access key> -e S3_SECRET_KEY=<s3 secret key> flight_db src/upload_data_to_s3.py 
```

Or you can do it this way:
```
export S3_PUBLIC_KEY=<your access key>
export S3_SECRET_KEY=<your secret key>
docker run flight_db src/upload_data_to_s3.py 
```

### 6. Create table in RDS or sqlite
This database is for storing user input in the flask app. 

 - If using RDS:
```buildoutcfg
docker run -it --env-file=.mysqlconfig flight_db src/flight_db.py rds --truncate
```

 - If using sqlite:
```buildoutcfg
docker run --env-file=.mysqlconfig --mount type=bind,source="$(pwd)"/data,target=/app/data flight_db src/flight_db.py sqlite --truncate
```
We set the --truncate flag so that we delete any existing rows in the table before adding new rows.  
Disregard logging information  on truncate errors (this happens when there are no existing rows); ingesting data should work properly.  
  
### 7. Doing SQL operations in MYSQL and check that table 'flight' exists
```bash
sh run_mysql_client.sh
USE msia423_db;
SELECT * FROM flight;
```

You should see one row of artificial data present in the flight table. 

## Directory Structure
<!-- toc -->
- [Project Charter](#project-charter) 
- [Planning](#planning)
- [Backlog](#backlog) 
- [Icebox](#icebox)
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


## Project Charter
### Vision
Flight delays can be attributed to many causes such as weather, military, technical issues, etc. As passengers, it helps to know beforehand whether and how long a flight will be delayed to avoid long wait times at airports. Passengers can also consult the app when purchasing flight tickets to select the flight that is least likely to experience delay. For airlines, getting a sense of what kinds of flights are more likely to be delayed for a long period of time may also be beneficial in terms of scheduling flight routes in the future. 

After the deployment of the app, airlines and third-party flight booking sites may purchase and incoporate the app into their ticketing systems to allow users to see delay predictions for every flight options. The template of the app may also be used in future flight-related research including jet bridge availability prediction, check-in wait time prediction, etc.  

### Mission
This project aims to create an interactive app that allows users to get a predicted delayed time (negative if predicted to be arriving early) for their upcoming flights based on attributes they enter including operating airlines, departing airports, flight time, day of week, etc. For example, a flight from LAX to ORD, scheduled flight time being 4 hours, schedule departure time being 7PM Sunday, may get a predicted delayed time of 45 minutes, while another flight in early morning on weekdays may get a much lower and even negative predicted delay time (meaning that the flight will arrive earlier than scheduled). 

Data from [Bureau of Transportation Statistics](https://www.transtats.bts.gov/DL_SelectFields.asp?Table_ID=236) are available for download and licensed for research usage. The data is available from 1987 to Jan 2020, from which we will select a timeframe of roughly 6 months to 1 year for modelling purpose. 

### Success Criteria
- Technical Criteria:
  - By splitting the dataset into train and test, we will define success in terms of a CV R-squared of more than 85% for the final deployed model.
  - We will also check that the RMSE in terms of minutes delayed is less than 30.   
- Business Criteria:
  - At least 50 percent of users who used the app once returned to the app for their next flight.  
  - 10% free-to-paid conversion rate.  
  - Daily active users (DAU) exceeds 1000.  

## Planning
### Initiative 1: Data Preparation and Model Building
- Epic 1: Build baseline model using linear regression 
  - Story 1: Understand the Data dictionary and perform exploratory data analysis
  - Story 2: Query the features relevant for prediction
  - Story 3: Feature engineering on variables of time and distance
  - Story 4: Build a linear regression model on the data
  - Story 5: Perform k-fold cross-validation on the data, generate evaluation metrics which will then be transformed into values corresponding to errors in delayed time. 
- Epic 2: Try other regression models and select best model based on performance jmetrics
  - Story 1: Use XGBoost/Random Forests on the data to predict delayed time. 
  - Story 2: Use Neural Network on the data to predict delayed time. 
  - Story 3: Perform k-fold cross-validation on the data to generate the performance metrics. Compare them with the ones from linear regression. 

### Initiative 2: Create Application and Perform Testing
- Epic 1: Construct the front-end of the application
  - Story 1: Create the framework of the front page of the application
  - Story 2: Create input boxes/sliders where users can interact with the application by filling out numbers/texts
  - Story 3: Create page for the result of the model (may be on the same page or a separate pop-up page)
 - Epic 2: Integrate the app with the selected back-end predictive model
   - Story 1: Construct database for user input and result
   - Story 2: Integrate the model into the app
  - Epic 3: Testing
    - Story 1: Write unit tests
    - Story 2: Revisit the model and make necessary changes based on test results
    - Story 3: Create method to monitor the performance of the app; change user interface if necessary

## Backlog
1. “Initiative1.epic1.story1” (1 point) - PLANNED
2. “Initiative1.epic1.story2” (1 point) - PLANNED
3. “Initiative1.epic1.story3” (2 point) - PLANNED
4. “Initiative1.epic1.story4” (4 point) - PLANNED
5. “Initiative1.epic1.story5” (4 point) - PLANNED
6. “Initiative2.epic1.story1” (4 point) - PLANNED
7. “Initiative1.epic2.story1” (2 point)
8. “Initiative1.epic2.story2” (2 point) 
9. “Initiative1.epic2.story3” (2 point) 
10. “Initiative2.epic1.story2” (4 point)
11. “Initiative2.epic1.story3” (4 point)

## Icebox
- “Initiative2.epic1.story2”
- “Initiative2.epic1.story3”
- “Initiative2.epic2.story1”
- “Initiative2.epic2.story2”
- “Initiative2.epic3.story1”
- “Initiative2.epic3.story2”
- “Initiative2.epic3.story3”


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

