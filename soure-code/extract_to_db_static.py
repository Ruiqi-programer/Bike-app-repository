import requests
import traceback
import datetime
import time
import os
import dbinfo
import json
from sqlalchemy import create_engine,text
import pymysql

def stations_to_db(text_data,in_engine):
    # let us load the stations from the text received from jcdecaux
    stations = json.loads(text_data)

    # print type of the stations object, and number of stations
    print(type(stations), len(stations))
    # let us print the type of the object stations (a dictionary) and load the content
    # now let us use the engine to insert into the stations

    insert=text(
        """
            INSERT INTO station (number,name,address, position_lat,position_lng, bonus,banking, bikestands) 
            VALUES (:number, :name, :address, :position_lat, :position_lng, :bonus, :banking, :bikestands);
            """
            #VALUES (%s, %s, %s, %s, %s);
            
    )
    with in_engine.connect() as conn:
        with conn.begin():  # 显式开启事务
            for station in stations:
                print(type(station))

                # let us load only the parts that we have included in our db:
                position=station.get("position")
                values = {
                        "number": int(station.get("number",0)),
                        "name": station.get("name", "Unnamed"),
                        "address": station.get("address", "Unknown"),
                        "position_lat":position.get("lat",0.0),
                        "position_lng":position.get("lng",0.0),
                        "bonus": bool(station.get("bonus", False)),
                        "banking": bool(station.get("banking", False)),
                        "bikestands": int(station.get("bike_stands", 0))
                    }
                conn.execute(insert,values)
            print("Stations inserted successfully.")



def main():
    USER = "root"
    PASSWORD = "656692"
    PORT = "3306"
    DB = "dublinbikesystem"
    URI = "localhost"

    connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)

    engine = create_engine(connection_string, echo = True)


    try:
        r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME})
        stations_to_db(r.text,engine)
    except:
        print(traceback.format_exc())

# CTRL + Z or CTRL + C to stop it
main()   