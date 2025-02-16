import dbinfo
import requests
import json
import sqlalchemy as sqla
from sqlalchemy import create_engine,text
import traceback
import glob
import os
from pprint import pprint
import simplejson as json
import time
from IPython.display import display


USER = "root"
PASSWORD = "656692"
PORT = "3306"
DB = "dublinbikesystem"
URI = "localhost"

connection_string = "mysql+pymysql://{}:{}@{}:{}".format(USER, PASSWORD, URI, PORT)
# Create database engine
engine = create_engine(connection_string, echo = True)


# Create database if it doesn't exist
with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB};"))

