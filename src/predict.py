from numpy import loadtxt
import pickle
import logging.config
import numpy as np
import logging

logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger('predict')

def predict(filename, flight):
    """
    load the model and predict the outcome and probabilities based on input Flight object
    :param filename: model path and filename
    :param flight: Flight object containing user input in html
    :return: label and probability of delay
    """
    logger.debug("Loading model pickle file ...")
    try:
        loaded_model = pickle.load(open(filename, 'rb'))
        logger.info("Successfully loaded model!")
    except pickle.UnpicklingError as e:
        # normal, somewhat expected
        logger.debug("Not able to unpickle model object!")
        pass
    except (AttributeError, EOFError, ImportError, IndexError) as e:
        # secondary errors
        logger.debug("Not able to unpickle model object!")

    unique_airlines, unique_orig, unique_dest = get_unique_items()

    airline = flight.airline
    air_time = flight.air_time
    origin = flight.origin_city
    dest = flight.dest_city
    dep_time = flight.dep_time
    month = flight.month
    dom = flight.day_of_month
    dow = flight.day_of_week

    features = []
    create_dummy_row(features, air_time, month, dom, dow, dep_time, airline, origin, dest, unique_airlines, unique_orig, unique_dest)

    label = loaded_model.predict(np.array(features).reshape(1, -1))[0]

    probs = loaded_model.predict_proba(np.array(features).reshape(1, -1))[0][0]

    if label == 'delay':
        label = 'delayed'

    return label, probs

def get_unique_items():
    """
    read in txt files of unique airline codes, origin and destination airports
    :return: lists of unique airlines, unique original airports and unique destination airports
    """
    try:
        with open("txt_files/airlines.txt") as f:
            unique_airlines = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        unique_airlines = [x.strip() for x in unique_airlines]
        f.close()

        with open("txt_files/origin.txt") as f:
            unique_orig = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        unique_orig = [x.strip() for x in unique_orig]
        f.close()

        with open("txt_files/dest.txt") as f:
            unique_dest = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        unique_dest = [x.strip() for x in unique_dest]
        f.close()

    except (AttributeError, EOFError, ImportError, IndexError) as e:
        logger.debug("Unable to load txt files!")

    return (unique_airlines, unique_orig, unique_dest)


def create_dummy_row(features, air_time, month, dom, dow, dep_time, airline, origin, dest, unique_airlines, unique_orig, unique_dest):
    """
    turn row of flight data into its dummy variable version
    :param features: empty list storing processed features
    :param air_time: schedule air time
    :param month: flight month
    :param dom: flight day of month
    :param dow: flight day of week
    :param dep_time: flight departure time in hour
    :param airline: airline code
    :param origin: original airport code
    :param dest: destination airport code
    :param unique_dest: list of unique destination airport codes
    :param unique_orig: list of unique origiinal airport codes
    :param unique_airlines: list of unique airline codes
    :return: None
    """

    features.append(air_time)
    try:
        for i in range(1, 13):
            if i == month:
                features.append(1)
            else:
                features.append(0)

        for i in range(1, 32):
            if i == dom:
                features.append(1)
            else:
                features.append(0)

        for i in range(1, 8):
            if i == dow:
                features.append(1)
            else:
                features.append(0)

        for i in range(0, 24):
            if i == dep_time:
                features.append(1)
            else:
                features.append(0)

        for i in unique_airlines:
            if i == airline:
                features.append(1)
            else:
                features.append(0)

        for i in unique_orig:
            if i == origin:
                features.append(1)
            else:
                features.append(0)

        for i in unique_dest:
            if i == dest:
                features.append(1)
            else:
                features.append(0)

    except (TypeError, AttributeError, EOFError, ImportError, IndexError) as e:
        logger.error("Unable to turn flight info into binary features!")
        return None



