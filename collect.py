# import csv
# import psycopg2
# import os
# from config import HOST, DATABASE, PORT, root_path
# from dotenv import load_dotenv

# load_dotenv()

# def connect_database():
#     connection = psycopg2.connect(
#         host = HOST,
#         database = DATABASE,
#         user  = os.getenv('USER_DB'),
#         password = os.getenv('PASSWORD'),
#         port = int(PORT)
#     )
#     return connection

# def collect_dealer():

#     with connect_database() as conn:
#         with conn.cursor() as cursor:
            
#             sql_query = """ SELECT * FROM DEALER"""
#             cursor.execute(sql_query)
            
#             columns = [desc[0] for desc in cursor.description]
            
#             rows = cursor.fetchall()

#             with open(root_path+'data/processed_data/clean/downloaded_dealer.csv','w',newline='') as f:
#                 writer = csv.DictWriter(f,fieldnames=columns)
#                 writer.writeheader()
                
#                 for row in rows:
#                     writer.writerow(dict(zip(columns,row)))
# if  __name__ == "__main__":
#     collect_dealer()