import csv
import psycopg2
import os
from config import HOST, USER_DATABASE, PORT, EXTRACTED_DEALER_FILE, EXTRACTED_INVENTORY_FILE, EXTRACTED_PRODUCTS_FILE
from dotenv import load_dotenv
from logger import log_error
load_dotenv()

def connect_database():
    connection = psycopg2.connect(
        host = HOST,
        database = USER_DATABASE,
        user  = os.getenv('USER_DB'),
        password = os.getenv('PASSWORD'),
        port = int(PORT)
    )
    return connection

def extract_dealer():
    
    sql_query = """ SELECT * FROM DEALER"""
    with connect_database() as conn:
        with conn.cursor() as cursor:
            
            try:
            
                cursor.execute(sql_query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()


                with open(EXTRACTED_DEALER_FILE,'w',newline='') as f:
                    writer = csv.DictWriter(f,fieldnames=columns)
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(dict(zip(columns,row)))
            except Exception as e:
                log_error(f"STAGE = EXTRACT | ERROR COLLECTING DEALER DATA: {e}")
                raise

def extract_products():
    
    sql_query = """SELECT * FROM PRODUCTS"""
    with connect_database() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(sql_query)
                columns = [desc[0] for desc in cursor.description]
                batch_size = 200
                with open(EXTRACTED_PRODUCTS_FILE,'w') as f_read:
                    writer = csv.DictWriter(f_read,fieldnames=columns)
                    writer.writeheader()
                    while True:
                        rows = cursor.fetchmany(batch_size)
                        if not rows:
                            break
                        for row in rows:
                            writer.writerow(dict(zip(columns,row)))
            except Exception as e:
                log_error(f'STAGE = EXTRACT | ERROR COLLECTING PRODUCTS DATA: {e}')
                raise

def extract_inventory():
    
    sql_query = """SELECT * FROM INVENTORY"""
    with connect_database() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(sql_query)
                columns = [desc[0] for desc in cursor.description]
                batch_size = 200
                with open(EXTRACTED_INVENTORY_FILE,'w') as f_read:
                    writer = csv.DictWriter(f_read,fieldnames=columns)
                    writer.writeheader()
                    while True:
                        rows = cursor.fetchmany(batch_size)
                        if not rows:
                            break
                        for row in rows:
                            writer.writerow(dict(zip(columns,row)))
            except Exception as e:
                log_error(f'STAGE = EXTRACT | ERROR COLLECTING INVENTORY DATA: {e}')
                raise


if  __name__ == "__main__":
    extract_dealer()
    extract_products()
    extract_inventory()