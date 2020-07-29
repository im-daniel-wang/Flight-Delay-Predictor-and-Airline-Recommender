import boto3
import os
import config
import logging.config

#S3_PUBLIC_KEY = config.S3_PUBLIC_KEY
#S3_SECRET_KEY = config.S3_SECRET_KEY
S3_PUBLIC_KEY = os.environ['S3_PUBLIC_KEY']
S3_SECRET_KEY = os.environ['S3_SECRET_KEY']
FILE_NAME = config.FILE_NAME
BUCKET_NAME = config.BUCKET_NAME
S3_OBJECT_NAME = config.S3_OBJECT_NAME

logging.config.fileConfig(config.LOGGING_CONFIG)
logger = logging.getLogger('upload_data_to_S3')


s3_client = boto3.client('s3', aws_access_key_id=S3_PUBLIC_KEY, aws_secret_access_key=S3_SECRET_KEY)

try:
    s3_client.upload_file(FILE_NAME, BUCKET_NAME, S3_OBJECT_NAME)
except ClientError as e:
    logging.error(e)
    pass
