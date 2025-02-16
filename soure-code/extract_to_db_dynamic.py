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
    availability= json.loads(text_data)

    # print type of the stations object, and number of stations
    print(type(availability), len(availability))
    # let us print the type of the object stations (a dictionary) and load the content
    # now let us use the engine to insert into the stations

    insert=text(
        """
            INSERT INTO availability (number,available_bikes, available_bike_stands, status,last_update) 
            VALUES (:number, :available_bikes, :available_bike_stands, :status, :last_update);
            """
            #VALUES (%s, %s, %s, %s, %s);
            
    )

    with in_engine.connect() as conn:
        with conn.begin():  # 显式开启事务
            for station in availability:
                print(type(station))

                # let us load only the parts that we have included in our db:
                
                values = {
                        "number": int(station.get("number",0)),
                        "available_bikes": int(station.get("available_bikes", 0)),
                        "available_bike_stands": int(station.get("available_bike_stands", 0)),
                        "status":station.get("lstatus","Unknown"),
                        "last_update":station.get("last_update",None)
                       
                    }
                conn.execute(insert,values)
            print("availability inserted successfully.")



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
        #time.sleep(5*60) # NOTE: if you are downloading static station data only, you need to do this just once!
    except:
        print(traceback.format_exc())

# CTRL + Z or CTRL + C to stop it
main()   