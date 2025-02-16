import dbinfo
import requests
import json
import sqlalchemy as sqla
from sqlalchemy import create_engine,text
import traceback
import glob
import os
from pprint import pprint
import time
from IPython.display import display


USER = "root"
PASSWORD = "656692"
PORT = "3306"
DB = "dublinbikesystem"
URI = "localhost"

connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT,DB)
# Create database engine
engine = create_engine(connection_string, echo = True)

#create tables
sql = '''
CREATE TABLE IF NOT EXISTS station (
number INTEGER PRIMARY KEY,
name VARCHAR(256) NOT NULL,
address VARCHAR(256), 
position_lat DOUBLE NOT NULL,
position_lng DOUBLE NOT NULL,
bonus BOOLEAN ,
banking BOOLEAN ,
bikestands INTEGER NOT NULL
);
'''

try:
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS station;"))
        #create tables
        conn.execute(text(sql))
        # Use the engine to execute the DESCRIBE command to inspect the table schema
        tab_structure=conn.execute(text("SHOW COLUMNS FROM station;"))

        # Fetch and print the result to see the columns of the table
        columns = tab_structure.fetchall()
        print(columns)
except Exception as e:
    print(e)
    


sql = """
CREATE TABLE IF NOT EXISTS availability (
number INTEGER PRIMARY KEY,
available_bikes INTEGER,
available_bike_stands INTEGER,
status VARCHAR(256),
last_update DATETIME NOT NULL,
FOREIGN KEY (number) REFERENCES station(number) ON DELETE CASCADE
);
"""
try:
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS availability;"))
        #create tables
        conn.execute(text(sql))
        # Use the engine to execute the DESCRIBE command to inspect the table schema
        tab_structure=conn.execute(text("SHOW COLUMNS FROM availability;"))
        # Fetch and print the result to see the columns of the table
        columns = tab_structure.fetchall()
        print(columns)

except Exception as e:
    print(e)