
BUCKET_NAME = "python-bootcamp-ankit"



#ROOT_PATH
root_path = '/Users/ankitpanda/Desktop/Python_Pipeline/project/'  


# DEALER CONFIG
DEALER_S3_KEY = "dirty/dealer.csv"
DEALER_LOCAL_FILE = root_path+"data/raw_data/dealer_downloaded.csv"

CLEAN_DEALER_FILE = "data/processed_data/clean/clean_dealer.csv"
REJECT_DEALER_FILE = "data/processed_data/rejected/reject_dealer.csv"
SUMMARY_DEALER_FILE = "data/processed_data/summary/dealer_summary.json"


# PRODUCT CONFIG
PRODUCT_S3_KEY = "dirty/product.csv"
PRODUCT_LOCAL_FILE = root_path+"data/raw_data/product_downloaded.csv"



CLEAN_PRODUCT_FILE =  root_path+"data/processed_data/clean/clean_product.csv"
REJECT_PRODUCT_FILE = root_path+"data/processed_data/rejected/reject_product.csv"
SUMMARY_PRODUCT_FILE = root_path+"data/processed_data/summary/product_summary.json"


# INVENTORY CONFIG
INVENTORY_S3_KEY = "dirty/inventory.csv"
INVENTORY_LOCAL_FILE = root_path+"data/raw_data/inventory_downloaded.csv"

CLEAN_INVENTORY_FILE =  root_path+"data/processed_data/clean/clean_inventory.csv"
REJECT_INVENTORY_FILE = root_path+"data/processed_data/rejected/reject_inventory.csv"
SUMMARY_INVENTORY_FILE = root_path+"data/processed_data/summary/inventory_summary.json"

SALES_S3_KEY = "dirty/sales_logs.jsonl"
SALES_LOCAL_FILE = root_path+"data/raw_data/sales_logs.jsonl"

CLEAN_SALES_LOGS_FILE =  root_path+"data/processed_data/clean/clean_sales_logs.jsonl"
REJECT_SALES_LOGS_FILE = root_path+"data/processed_data/rejected/reject_sales_logs.jsonl"
SUMMARY_SALES_LOGS_FILE = root_path+"data/processed_data/summary/sales_logs_summary.json"

HOST="localhost"
DATABASE="python_bootcamp"
PORT=5432