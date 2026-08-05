import os 
import psycopg2
from dotenv import load_dotenv
import csv
from config import CLEAN_DEALER_FILE,CLEAN_PRODUCT_FILE,CLEAN_INVENTORY_FILE, HOST, USER_DATABASE, PORT
from functools import wraps
import time
from logger import log_error,log_info,log_warning
# CONFIGURATION OF VARIABLES AND CONNECTION WITH POSTGRESQL
load_dotenv()

 


# Retry Resilience Function 
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

@retry()
def connect_database():
    connection = psycopg2.connect(
            host = HOST,
            database =USER_DATABASE,
            user  = os.getenv('USER_DB'),
            password = os.getenv('PASSWORD'),
            port = int(PORT)
        )
    return connection

# RECORD THE LOAD TRACKING TABLE
def load_tracking(file_name,file_hash):
    
    def record_processing(cursor, file_name, file_hash):
        cursor.execute(
            """INSERT INTO load_tracking 
            (file_name, file_hash, processed_timestamp) 
            VALUES (%s, %s, NOW())""",
            (file_name, file_hash)
        )
    conn = connect_database()
    cursor = conn.cursor()
    record_processing(cursor,file_name,file_hash)


#--------------------------------------
#------------__DEALER LOAD___----------
#---------------------------------------
def insert_dealer():

    connection = connect_database()
    
    def insert_into_dealer(connection, dealer_id,  dealer_code, dealer_name, city, state, region, dealer_type,created_date
                           ,is_active,email,phone, credit_terms_days):
        
     
        sql = """
            INSERT INTO DEALER 
            (dealer_id,  dealer_code, dealer_name, city, state, region, dealer_type, created_date, is_active, email, phone, credit_terms_days)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        with connection.cursor() as cursor:
            cursor.execute(sql,(dealer_id,  dealer_code, dealer_name, city, state, region, dealer_type,created_date,is_active,email,phone, credit_terms_days))
        
    log_info(f'STAGE = LOAD | LOADING DATA INTO DEALER TABLE')
    def insert_data_into_dealer(connection):
        try:
            with open(CLEAN_DEALER_FILE) as f_read:
                rows = csv.DictReader(f_read)
                for row in rows:
                    insert_into_dealer(connection,
                                       row.get('dealer_id'),row.get('dealer_code'),
                                       row.get('dealer_name'),row.get('city'),
                                       row.get('state'),row.get('region'),
                                       row.get('dealer_type'),row.get('created_date'),
                                       row.get('is_active'),row.get('email'),
                                       row.get('phone'),row.get('credit_terms_days'))
            connection.commit()
            log_info(f'STAGE = LOAD | SUCCESSFULLY LOADED DATA INTO DEALER TABLE')
        except Exception as e:
            connection.rollback()
            log_error(f'STAGE = LOAD | ERROR IN LOADING DATA {e}')
            raise
        finally:
            connection.close()
    insert_data_into_dealer(connection)
    
#--------------------------------------
#------------__PRODUCT LOAD___----------
#---------------------------------------

def insert_product():
    
    connection = connect_database()
    batch_size = 200
    cursor = connection.cursor()
    product_data = []
    log_info(f'STAGE = LOAD | LOADING DATA INTO PRODUCTS TABLE')
    try: 
        with open(CLEAN_PRODUCT_FILE) as f_read:
            rows = csv.DictReader(f_read)
            for row in rows:
                product_data.append(row)
    except Exception as e:
        log_error(f'STAGE = LOAD |  ERROR READING PRODUCT CSV FILE  ')
        
    sql = """
        INSERT INTO PRODUCTS(product_id,sku,product_name,category,subcategory,brand,uom,unit_cost,unit_price,weight_kg,is_discontinued,created_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
    """
    
    for i in range(0,len(product_data),batch_size):
        batch = product_data[i:batch_size+i]
        batch_tuples = [
            (
                row.get('product_id'),
                row.get('sku'),
                row.get('product_name'),
                row.get('category'),
                row.get('subcategory'),
                row.get('brand'),
                row.get('uom'),
                row.get('unit_cost'),
                row.get('unit_price'),
                row.get('weight_kg'),
                row.get('is_discontinued'),
                row.get('created_date')
            )
            for row in batch
        ]
        try:
            cursor.executemany(sql,batch_tuples)
            connection.commit()
            log_info(f"Batch {i // batch_size + 1}: Inserted {len(batch)} rows")

                
        except Exception as e:
            connection.rollback()
            log_error(f'STAGE = LOAD | ERROR LOADING DATA {e}')
            raise
    cursor.close()
    connection.close()
# insert_product()

#--------------------------------------
#----------__INVENTORY LOAD___----------
#---------------------------------------

def insert_inventory():
    
    connection = connect_database()
    batch_size = 200
    cursor = connection.cursor()
    inventory_data = []
    
    try: 
        with open(CLEAN_INVENTORY_FILE) as f_read:
            rows = csv.DictReader(f_read)
            for row in rows:
                inventory_data.append(row)
    except Exception as e:
        log_info(f'STAGE = LOAD | ERROR READING INVENTORY CSV FILE')
        
    sql = """
        INSERT INTO INVENTORY(inventory_id,snapshot_date,dealer_id,product_id,on_hand_qty,on_order_qty,reorder_point,reorder_qty,last_restock_date,last_sale_date)
        VALUES (%s,to_date(%s,'DD-MM-YYYY'),%s,%s,%s,%s,%s,%s,to_date(%s,'DD-MM-YYYY'),to_date(%s,'DD-MM-YYYY')) 
    """

    log_info(f'STAGE = LOAD | LOADING DATA INTO INVENTORY TABLE')
    for i in range(0,len(inventory_data),batch_size):
        batch = inventory_data[i:batch_size+i]
        batch_tuples = [
            (
                row.get('inventory_id'),
                row.get('snapshot_date'),
                row.get('dealer_id'),
                row.get('product_id'),
                row.get('on_hand_qty'),
                row.get('on_order_qty'),
                row.get('reorder_point'),
                row.get('reorder_qty'),
                row.get('last_restock_date'),
                row.get('last_sale_date')
            )
            for row in batch
        ]
        try:
            cursor.executemany(sql,batch_tuples)
            connection.commit()
            log_info(f"Batch {i // batch_size + 1}: Inserted {len(batch)} rows")
            log_info(f'STAGE = LOAD | SUCCESSFULLY LOADED DATA INTO INVENTORY TABLE')

        
        except Exception as e:
            connection.rollback()
            log_error(f'STAGE = LOAD | ERROR IN LOADIND DATA {e}')
            raise
    cursor.close()
    connection.close()
# insert_inventory()