import logging

import yaml
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def clean(dat, dummy, drop_column):
    """
    clean the flights dataset and create additional attributes for modelling
    """
    unique_airline = sorted(dat.OP_UNIQUE_CARRIER.unique().tolist())
    unique_origin = sorted(dat.ORIGIN.unique().tolist())
    unique_dest = sorted(dat.DEST.unique().tolist())

    with open('txt_files/airlines.txt', 'w') as f:
        for item in unique_airline:
            f.write("%s\n" % item)
    with open('txt_files/origin.txt', 'w') as f:
        for item in unique_origin:
            f.write("%s\n" % item)
    with open('txt_files/dest.txt', 'w') as f:
        for item in unique_dest:
            f.write("%s\n" % item)

    dat = dat.dropna()
    dat = dat.iloc[:, 2:]

    dat['dep_hour'] = get_dept_hour_bucket(dat)

    dat['length'] = get_length(dat)

    dat = pd.get_dummies(dat, columns=dummy)

    dat = dat.drop(columns=drop_column)

    dat['delay'] = get_binary(dat)

    dat = dat.drop(columns=['DEP_DELAY'])

    return dat


def get_dept_hour_bucket(dat):
    try:
        res = np.where(dat['CRS_DEP_TIME'].astype('str').str.len() > 2, np.where(dat['CRS_DEP_TIME'].astype('str').str.len() == 3 , \
                                                                              '0' + dat['CRS_DEP_TIME'].astype('str').str.slice(0, -2), \
                                                                              dat['CRS_DEP_TIME'].astype('str').str.slice(0, -2)), '0')
        return res

    except KeyError:
        logger.info("Column does not exist, failed to derive attribute")
        pass

def get_length(dat):
    try:
        res = dat['CRS_ELAPSED_TIME'] // 60
        return res

    except KeyError:
        logger.info("Column does not exist, failed to derive attribute")
        pass

def get_binary(dat):
    try:
        res = np.where(dat['DEP_DELAY'] > 0, 'delay', 'on_time')
        return res
    except KeyError:
        logger.info("Target column does not exist. ")

if __name__ == "__main__":
    d = {"DEP_DELAY": [1, -5, 4, 6, -7, 2, -2]}
    df = pd.DataFrame(d)
    print(get_binary(df))
