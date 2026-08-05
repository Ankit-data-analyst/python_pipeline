import boto3 
from dotenv import load_dotenv
import os
import time
from logger import log_info,log_error
from functools import wraps
from config import BUCKET_NAME,EXTRACTED_DEALER_FILE, EXTRACTED_PRODUCTS_FILE, EXTRACTED_INVENTORY_FILE, EXTRACT_DEALER_KEY, EXTRACT_PRODUCTS_KEY, EXTRACT_INVENTORY_KEY
from logger import log_error
load_dotenv()


#Adding the retry resilience funciton 
def retry(max_attempts=3, delay=2):
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as e:

                    if attempt == max_attempts - 1:
                        log_error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise

                    backoff = delay * (2 ** attempt)

                    log_info(
                        f"{func.__name__} failed (Attempt {attempt + 1}/{max_attempts}). "
                        f"Retrying in {backoff} seconds..."
                    )

                    time.sleep(backoff)

        return wrapper

    return decorator

    
def initialize_boto3():
    s3 = boto3.client(
        's3',
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name = os.getenv('AWS_REGION')
    )
    return s3

@retry()
def upload_to_s3(localpath,BUCKET_NAME,S3_KEY):
    s3 = initialize_boto3()
    try:
        log_info(f'STAGE = UPLOAD | UPLOADING FILE:{S3_KEY}')
        s3.upload_file(localpath,BUCKET_NAME,S3_KEY)
        log_info(f'STAGE = INGEST | SUCCESSFULLY UPLOADED {S3_KEY}')
    except Exception as e:
        log_error(f'Failed to upload {S3_KEY}:{e}')
        raise

def dealer_upload():
    upload_to_s3(EXTRACTED_DEALER_FILE,BUCKET_NAME,EXTRACT_DEALER_KEY)
    
def product_upload():
    upload_to_s3(EXTRACTED_PRODUCTS_FILE,BUCKET_NAME, EXTRACT_PRODUCTS_KEY )

def inventory_upload():
    upload_to_s3(EXTRACTED_INVENTORY_FILE, BUCKET_NAME, EXTRACT_INVENTORY_KEY)
    
if __name__ == '__main__':
    dealer_upload()
    product_upload()
    inventory_upload()