import boto3
import os
import config
import logging.config
import logging

logger = logging.getLogger(__name__)

def acquire(S3_PUBLIC_KEY, S3_SECRET_KEY, FILE_NAME, BUCKET_NAME, S3_OBJECT_NAME):
    """
    acquiring data and download it to specified folder location
    :param S3_PUBLIC_KEY: S3 public key obtained from environment variable
    :param S3_SECRET_KEY: S3 secret key obtained from environment variable
    :param FILE_NAME: path of where you want to put the downloaded file
    :param BUCKET_NAME: name of the S3 bucket to download file from
    :param S3_OBJECT_NAME: path of the file in the S3 bucket
    """
    try:
        s3_client = boto3.client('s3', aws_access_key_id=S3_PUBLIC_KEY, aws_secret_access_key=S3_SECRET_KEY)
        s3_client.download_file(BUCKET_NAME, S3_OBJECT_NAME, FILE_NAME)

    except ClientError as e:
        logger.error("Missing credentials, cannot connect to S3 bucket")
        pass

    except ParamValidationError as e:
        logger.error("Wrong parameters set!")
        pass

