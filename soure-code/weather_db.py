import requests
import traceback
import datetime
import time
import os
import dbinfo
import json
from sqlalchemy import create_engine,text
import pymysql
import sys


#create tables
def create_current_table(in_engine):
    sql = text('''
    CREATE TABLE IF NOT EXISTS current (
        dt DATETIME NOT NULL,
        sunrise DATETIME,
        sunset DATETIME,
        temp FLOAT,
        feels_like FLOAT,
        humidity INTEGER,
        pressure INTEGER,
        dew_point FLOAT,
        uvi FLOAT,
        weather_id INTEGER,
        weather_description VARCHAR(256),
        wind_deg FLOAT,
        wind_speed FLOAT,
        visibility INTEGER,
        PRIMARY KEY (dt)
    );
    ''')
 
    with in_engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS current;"))
        #create tables
        conn.execute(sql)
        # Use the engine to execute the DESCRIBE command to inspect the table schema
        # tab_structure=conn.execute(text("SHOW COLUMNS FROM station;"))
        # # Fetch and print the result to see the columns of the table
        # columns = tab_structure.fetchall()
        # print(columns)



def current_table_to_db(text_data,in_engine):
    # let us load the stations from the text received from jcdecaux
    weather = json.loads(text_data)
    current=weather.get("current")
    insert=text(
        """
            INSERT INTO current (dt,sunrise,sunset, temp,feels_like, humidity,pressure, dew_point,uvi,weather_id,weather_description,wind_deg,wind_speed,visibility) 
            VALUES (:dt, :sunrise, :sunset, :temp, :feels_like, :humidity, :pressure, :dew_point, :uvi, :weather_id, :weather_description, :wind_deg, :wind_speed, :visibility);
            """
            
    )
    with in_engine.connect() as conn:
        with conn.begin():  # 显式开启事务
            dt_timestamp = current.get("dt", 0)/1000  
            dt_sunrise_timestamp = current.get("sunrise", 0)/1000  
            dt_sunset_timestamp = current.get("sunset", 0)/1000  
            dt = datetime.datetime.fromtimestamp(dt_timestamp, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
            dt_sunrise = datetime.datetime.fromtimestamp(dt_sunrise_timestamp, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
            dt_sunset = datetime.datetime.fromtimestamp(dt_sunset_timestamp, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S')
            weather_info=current.get("weather")
            values = {
                    "dt": dt,
                    "sunrise":dt_sunrise,
                    "sunset": dt_sunset,
                    "temp":float(current.get("temp",0.0)),
                    "feels_like":float(current.get("feels_like",0.0)),
                    "humidity": int(current.get("humidity")),
                    "pressure": int(current.get("pressure")),
                    "dew_point": float(current.get("dew_point", 0)),
                    "uvi": float(current.get("uvi")),
                    "weather_id": int(weather_info[0].get("id")),
                    "weather_description": weather_info[0].get("description"),
                    "wind_deg": float(current.get("wind_deg")),
                    "wind_speed": float(current.get("wind_speed")),
                    "visibility": int(current.get("visibility"))
                }
            conn.execute(insert,values)
        print("Current weather inserted successfully.")



def main():
    USER = "root"
    PASSWORD = ""
    PORT = "3306"
    DB = "dublinbikesystem"
    URI = "localhost"

    connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)
    engine = create_engine(connection_string, echo = True)

    API_KEY = "a39626f86048c97dbd2da2d0c5b7e67d"  
    lat=53.3498
    lon=-6.2603
    part="minutely,alerts"
    URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API_KEY}"
    
    create_current_table(engine)
    while True:
        try:
            r = requests.get(URL)
            current_table_to_db(r.text,engine)
            print("Waiting for the next update in 1 hour...")
            time.sleep(5*60)  # Wait 1 hour before fetching new data
        except KeyboardInterrupt:
            print("\nmannually kill the program")
            sys.exit(0)
        except:
            print(traceback.format_exc())

# CTRL + Z or CTRL + C to stop it
main()   
