import sklearn
from sklearn import model_selection
from sklearn import linear_model
from sklearn import metrics
from sklearn.model_selection import train_test_split
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import argparse
import yaml
import logging
from sklearn import tree

logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger('train')


def train_model(dat, test_size, target_col, max_depth):
    """
    train a decision tree model on the input data
    :param dat: input dataframe containing both features and classes
    :param test_size: test size for train test split
    :param target_col: the column used for label
    :max_depth: maximum depth of decision tree
    """
    try:
        target = dat[target_col]
        features = dat.drop(columns=target_col)

        X_train, X_test, y_train, y_test = trainTestSplit(features, target, test_size)
    except KeyError:
        logger.error("Unable to locate target column!")
        return None
    clf = tree.DecisionTreeClassifier(max_depth = max_depth)
    clf = clf.fit(X_train, y_train)
    return clf


def trainTestSplit(features, target, test_size):
    """
    split the data into train and test based on test_size given
    :param features: dataframe for feature columns
    :param target: series of classes
    :param test_size: ratio of test size
    :return: features and classes after splitting according to test size
    """
    return train_test_split(features, target, test_size=test_size)
