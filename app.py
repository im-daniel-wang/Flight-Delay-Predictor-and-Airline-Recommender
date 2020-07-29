import traceback
from flask import render_template, request, redirect, url_for
import logging.config
from flask import Flask
from src.predict import predict
from flask_sqlalchemy import SQLAlchemy
import os

from src.flight_db import Flight

# Initialize the Flask application
app = Flask(__name__, template_folder="app/templates")

# Configure flask app from flask_config.py
app.config.from_pyfile('config/flaskconfig.py')

# Define LOGGING_CONFIG in flask_config.py - path to config file for setting
# up the logger (e.g. config/logging/local.conf)
logging.config.fileConfig(app.config["LOGGING_CONFIG"])
logger = logging.getLogger(app.config["APP_NAME"])
logger.debug('Test log')

# Initialize the database
db = SQLAlchemy(app)


@app.route('/')
def index():
    """Main view that lists songs in the database.

    Create view into index page that uses data queried from Track database and
    inserts it into the msiapp/templates/index.html template.

    Returns: rendered html template

    """

    try:
        # flights = db.session.query(Flight).limit(app.config["MAX_ROWS_SHOW"]).all()
        logger.debug("Index page accessed")
        return render_template('index.html')
    except:
        traceback.print_exc()
        logger.warning("Not able to display tracks, error page returned")
        return render_template('error.html')


@app.route('/add', methods=['POST'])
def add_entry():
    """View that process a POST with new song input

    :return: redirect to index page
    """
    try:
        flight1 = Flight(month=request.form['month'], day_of_week=request.form['day_of_week'], day_of_month=request.form['day_of_month'], \
                         airline=request.form['airline'], origin_city=request.form['origin_city'], dest_city=request.form['dest_city'], \
                         dep_time=request.form['dept_time'], air_time=request.form['air_time'])
    except:
        logger.info("Unable to create flight")
    label = ""
    probs = 0
    try:
        label, probs = predict('data/tree.pkl', flight1)
    except Exception:
        logger.info("Unable to predict")
    logger.info("You are connecting to: " + app.config['SQLALCHEMY_DATABASE_URI'])
    try:
        db.session.add(flight1)
        db.session.commit()
    except Exception:
        logger.info("Cannot add row of flight data to the database! ")
        return render_template('error.html')
    logger.info("User input added to %s: %s from %s", app.config["SQLALCHEMY_DATABASE_URI"], request.form['airline'], request.form['origin_city'])
    return render_template('index.html', prediction_text='{}'.format(label), prob_text='{}'.format(probs))
    #return render_template('index.html', prediction_text=''.format(label), prob_text=''.format(probs))


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"], host=app.config["HOST"])