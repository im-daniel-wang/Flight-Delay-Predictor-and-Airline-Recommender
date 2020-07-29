#!/usr/bin/env bash
# Downloading file from S3 Bucket
python3 run.py acquire --config=config/test.yaml

# Generate features
python3 run.py clean --input=data/external/sample.csv --config=config/test.yaml --output=data/cleaned.csv

# Train Model
python3 run.py train --input=data/cleaned.csv --config=config/test.yaml --output=data/tree.pkl