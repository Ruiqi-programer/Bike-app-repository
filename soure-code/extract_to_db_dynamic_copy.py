import requests
import traceback
import datetime
import time
import os
import dbinfo
import json
from sqlalchemy import create_engine,text
import pymysql

def station_id_table(station_id, in_engine):
    table_name = f"availability_{station_id}"
    
    create_table_sql = text(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER AUTO_INCREMENT PRIMARY KEY,
            number INTEGER NOT NULL,
            available_bikes INTEGER,
            available_bike_stands INTEGER,
            status VARCHAR(256),
            last_update DATETIME NOT NULL,
            FOREIGN KEY (number) REFERENCES station(number) ON DELETE CASCADE
        );
    """)
     
    with in_engine.connect() as conn:
        conn.execute(create_table_sql)
    print(f"Table created: {table_name}")

def insert_availability_data(station, in_engine):
    station_id = station.get("number", 0)
    table_name = f"availability_{station_id}"

    last_update_timestamp = station.get("last_update", 0)/1000  # Example: 1707139200000 (milliseconds)
    last_update_dt = datetime.datetime.fromtimestamp(last_update_timestamp, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')

    values = {
        "number": int(station.get("number",0)),
        "available_bikes": int(station.get("available_bikes", 0)),
        "available_bike_stands": int(station.get("available_bike_stands", 0)),
        "status": station.get("status", "UNKNOWN"),
        "last_update": last_update_dt
    }

    insert_sql = text(f"""
        INSERT INTO {table_name} (number,available_bikes, available_bike_stands, status, last_update) 
        VALUES (:number, :available_bikes, :available_bike_stands, :status, :last_update);
    """)

    with in_engine.connect() as conn:
        with conn.begin():  # 显式开启事务
            conn.execute(insert_sql, values)
    print(f"Data inserted into {table_name}")

def fetch_and_store_data(in_engine):
    try:
        response = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})
        
        print("API 响应状态：", response.status_code)
        if response.status_code != 200:
            print("❌ API request failed. Check API key or contract name.")
            return
        availability_data =json.loads(response.text)
        
        for station in availability_data:
            station_id = station.get("number", 0)
            station_id_table(station_id, in_engine)  # Ensure the table exists
            insert_availability_data(station, in_engine)  # Insert real-time data
        
        print("All stations updated successfully.")

    except Exception as e:
        print("Error fetching data:", traceback.format_exc())

def main():
    USER = "root"
    PASSWORD = "656692"
    PORT = "3306"
    DB = "dublinbikesystem"
    URI = "localhost"

    connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{URI}:{PORT}/{DB}"
    engine = create_engine(connection_string, echo=False)

    while True:
        fetch_and_store_data(engine)
        print("Waiting for the next update in 1 hour...")
        time.sleep(5*60)  # Wait 1 hour before fetching new data


if __name__ == "__main__":
    main()