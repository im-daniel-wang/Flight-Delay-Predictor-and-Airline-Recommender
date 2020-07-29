import argparse
import logging
import os
import src.config as config

import yaml
import pandas as pd

import pickle

logging.basicConfig(format='%(name)-12s %(levelname)-8s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('run_pipeline')

from src.transform import clean
from src.train import train_model
from src.acquire import acquire


# fetching S3 bucket credentials from environment variables

S3_PUBLIC_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
S3_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
FILE_NAME = config.FILE_NAME
BUCKET_NAME = config.BUCKET_NAME
S3_OBJECT_NAME = config.S3_OBJECT_NAME



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Acquire, clean, create features, and model from clouds data")

    parser.add_argument('step', help='Which step to run', choices=['acquire', 'clean', 'train'])
    parser.add_argument('--acquire', '-a', default=None, help='Path to acquire data from S3')
    parser.add_argument('--input', '-i', default=None, help='Path to input data')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--output', '-o', default=None, help='Path to save output CSV (optional, default = None)')

    logger.info("arguments passed!")
    args = parser.parse_args()

    # Load configuration file for parameters and tmo path
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info("Configuration file loaded from %s" % args.config)

    # Load input file
    if args.input is not None:
        input = pd.read_csv(args.input)
        logger.info('Input data loaded from %s', args.input)

    # acquire data from S3 and download it to the specified folder
    if args.step == 'acquire':
        try:
            output = acquire(S3_PUBLIC_KEY, S3_SECRET_KEY, FILE_NAME, BUCKET_NAME, S3_OBJECT_NAME)
            logger.info("Dataset is successfully downloaded from S3 bucket! ")
        except Exception:
            logger.error("Could not open S3 connections given the input credentials! ")

    # clean the dataset
    if args.step == 'clean':
        output = clean(input, **config['transform']['clean'])
        logger.info("Finished cleaning the raw dataset!")
        if args.output is not None:
            output.to_csv(args.output, index=False, header = True)
            logger.info("Output saved to %s" % args.output)
            
    # train the model
    elif args.step == 'train':
        output = train_model(input, **config['train']['train_model'])
        logger.info("Finished training the model!")
        if args.output is not None:
            pickle.dump(output, open(args.output, "wb"))
            logger.info("Model saved to %s" % args.output)

