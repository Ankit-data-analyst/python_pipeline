import os 
from dotenv import load_dotenv
import boto3 
import hashlib
import psycopg2

from config import BUCKET_NAME, DEALER_S3_KEY, DEALER_LOCAL_FILE
from config import PRODUCT_S3_KEY, PRODUCT_LOCAL_FILE
from config import INVENTORY_S3_KEY, INVENTORY_LOCAL_FILE
from config import SALES_S3_KEY, SALES_LOCAL_FILE
from config import HOST,USER_DATABASE,PORT
from logger import log_info,log_error
import time
from functools import wraps

# CONFIGURATION OF ENVIRONMENT VARIABLES
load_dotenv()



# Generate the file hash 
def generate_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()

# Load Tracking Table

# Check if the file is already processed
def already_processed(cursor, file_hash):
    cursor.execute(
        "SELECT 1 FROM load_tracking WHERE file_hash = %s",
        (file_hash,)
    )
    return cursor.fetchone() is not None

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

# Connect to the database
@retry()
def connect_database():
    log_info(f"STAGE = INGEST | ESTABLISHING CONNECTION WITH THE DATABASE")
    connection = psycopg2.connect(
            host = HOST,
            database = USER_DATABASE,
            user  = os.getenv('USER_DB'),
            password = os.getenv('PASSWORD'),
            port = int(PORT)
        )
    log_info(f"STAGE = INGEST | CONNECTION ESTABLISHED SUCCESSFULLY")
    return connection

# INITIALIZING BOTO3 
def initialize_boto3():
    log_info(f'STAGE = INGEST | CONNECTION TO S3')
    s3 = boto3.client(
        's3',
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name = os.getenv('AWS_REGION')
    )
    log_info(f'STAGE = INGEST | CONNECTION WITH S3 ESTABLISHED SUCCESSFULLY')
    return s3

# DOWNLOADING FROM s3
@retry()
def download_from_s3(bucket_name,s3_key,path):
    s3 = initialize_boto3()
    try:
        log_info(f'STAGE = INGEST | DOWNLOADING FILE:{s3_key}')
        s3.download_file(bucket_name,s3_key,path)
        log_info(f'STAGE = INGEST | SUCCESSFULLY DOWNLOADED {s3_key}')
    except Exception as e:
        log_error(f'Download Failed for {s3_key}: {e}') 
        raise
       
        
## INGESTION FOR DEALER FILE 
def dealer_ingest():
    download_from_s3(BUCKET_NAME,DEALER_S3_KEY,DEALER_LOCAL_FILE)
    log_info(f'STAGE = INGEST | Generating file hash for {DEALER_LOCAL_FILE}')
    dealer_hash = generate_file_hash(DEALER_LOCAL_FILE)
    with connect_database() as connection:
        with connection.cursor() as cursor:
            log_info(f'STAGE = INGEST | Checking if {DEALER_LOCAL_FILE} is already processed')
            processed = already_processed(cursor,dealer_hash)  
    return processed,dealer_hash,DEALER_LOCAL_FILE

## INGESTION FOR PRODUCT FILE 
def product_ingest():
    download_from_s3(BUCKET_NAME,PRODUCT_S3_KEY,PRODUCT_LOCAL_FILE)

    log_info(f'STAGE = INGEST | Generating file hash for {PRODUCT_LOCAL_FILE}')
    product_hash = generate_file_hash(PRODUCT_LOCAL_FILE)
    with connect_database() as connection:
        with connection.cursor() as cursor:
            log_info(f'STAGE = INGEST | Checking if {PRODUCT_LOCAL_FILE} is already processed')
            processed = already_processed(cursor,product_hash)
    return processed,product_hash,PRODUCT_LOCAL_FILE
    
## INGESTION FOR INVENTORY FILE 
def inventory_ingest():
    download_from_s3(BUCKET_NAME,INVENTORY_S3_KEY,INVENTORY_LOCAL_FILE)

    log_info(f'STAGE = INGEST | Generating file hash for {INVENTORY_LOCAL_FILE}')
    inventory_hash = generate_file_hash(INVENTORY_LOCAL_FILE)
    with connect_database() as connection:
        with connection.cursor() as cursor:
            log_info(f'STAGE = INGEST | Checking if {INVENTORY_LOCAL_FILE} is already processed')
            processed = already_processed(cursor,inventory_hash)
    return processed, inventory_hash, INVENTORY_LOCAL_FILE

## INGESTION FOR SALES LOGS FILE
def sales_logs_ingest():
    download_from_s3(BUCKET_NAME,SALES_S3_KEY,SALES_LOCAL_FILE)
    

