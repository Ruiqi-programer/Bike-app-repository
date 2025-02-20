import db
import requests
import logging
from sqlalchemy import create_engine, text
import time
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from config import DB_CONFIG, BIKE_API_URL, WEATHER_API_URL

# Configure logging
logging.basicConfig(
    filename="app.log", 
    level=logging.INFO,  # Log only INFO level and above
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Connect to MySQL database
connection_string = f"mysql+mysqldb://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string, echo=True)

def convert_timestamp(unix_timestamp):
    """Convert Unix timestamp to MySQL DATETIME format."""
    return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')

def update_bike_data():
    """Fetch bike station data and update database."""
    try:
        response = requests.get(BIKE_API_URL, timeout=10)
        response.raise_for_status()
        stations = response.json()

        with engine.connect() as connection:
            transaction = connection.begin()
            for station in stations:
                static_sql = text("""
                    INSERT INTO stations (station_id, contract_name, name, address, latitude, longitude, total_bike_stands)
                    VALUES (:station_id, :contract_name, :name, :address, :latitude, :longitude, :total_bike_stands)
                    ON DUPLICATE KEY UPDATE name=VALUES(name), address=VALUES(address), total_bike_stands=VALUES(total_bike_stands)
                """)
                connection.execute(static_sql, {
                    "station_id": station["number"],
                    "contract_name": station["contract_name"],
                    "name": station["name"],
                    "address": station["address"],
                    "latitude": station["position"]["lat"],
                    "longitude": station["position"]["lng"],
                    "total_bike_stands": station["bike_stands"]
                })

                dynamic_sql = text("""
                    INSERT INTO station_status (station_id, available_bikes, available_bike_stands, status, last_update)
                    VALUES (:station_id, :available_bikes, :available_bike_stands, :status, :last_update)
                    ON DUPLICATE KEY UPDATE available_bikes=VALUES(available_bikes), available_bike_stands=VALUES(available_bike_stands), status=VALUES(status), last_update=VALUES(last_update)
                """)
                connection.execute(dynamic_sql, {
                    "station_id": station["number"],
                    "available_bikes": station["available_bikes"],
                    "available_bike_stands": station["available_bike_stands"],
                    "status": station["status"],
                    "last_update": convert_timestamp(station["last_update"] / 1000)
                })

            transaction.commit()
        logging.info("Bike data updated successfully.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Bike API Request Error: {e}")

def update_weather_data():
    """Fetch weather data and store in database."""
    try:
        response = requests.get(WEATHER_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        logging.info(f"Fetched weather data: {data}")  # Log weather data

        weather_sql = text("""
            INSERT INTO weather (timestamp, temp, feels_like, temp_min, temp_max, pressure, humidity, wind_speed, wind_gust, visibility, clouds, sunrise, sunset)
            VALUES (:timestamp, :temp, :feels_like, :temp_min, :temp_max, :pressure, :humidity, :wind_speed, :wind_gust, :visibility, :clouds, :sunrise, :sunset)
            ON DUPLICATE KEY UPDATE temp=VALUES(temp), feels_like=VALUES(feels_like), humidity=VALUES(humidity), wind_speed=VALUES(wind_speed)
        """)

        with engine.connect() as connection:
            try:
                logging.info(f"Executing SQL: {weather_sql}")  # Log SQL statement
                logging.info(f"Data being inserted: {data}")   # Log data

                connection.execute(weather_sql, {
                    "timestamp": datetime.utcnow(),
                    "temp": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "temp_min": data["main"]["temp_min"],
                    "temp_max": data["main"]["temp_max"],
                    "pressure": data["main"]["pressure"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"],
                    "wind_gust": data["wind"].get("gust"),
                    "visibility": data.get("visibility"),
                    "clouds": data["clouds"]["all"],
                    "sunrise": convert_timestamp(data["sys"]["sunrise"]),
                    "sunset": convert_timestamp(data["sys"]["sunset"])
                })
                
                connection.commit() 
                logging.info("Weather data updated successfully.")

            except SQLAlchemyError as e:
                logging.error(f"SQL Error: {e}")
                connection.rollback()  # Rollback on failure

    except requests.exceptions.RequestException as e:
        logging.error(f"Weather API Request Error: {e}")

import time
import logging

bike_update_interval = 5 * 60  # 5 minutes in seconds
weather_update_interval = 60 * 60  # 1 hour in seconds

counter = 0  # Track elapsed time

while True: # bike data updates evey 5 mins, weather updates every hour
    update_bike_data()

    if counter % weather_update_interval == 0:
        update_weather_data()

    counter += bike_update_interval
    logging.info("Waiting for the next bike update in 5 minutes...")
    time.sleep(bike_update_interval)
