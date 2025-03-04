import requests
import mysql.connector
import time
import os
import json
from datetime import datetime
from config import DB_CONFIG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenWeather API Configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
LAT = os.getenv("LAT", "53.350140")  # Default Dublin latitude
LON = os.getenv("LON", "-6.266155")  # Default Dublin longitude
WEATHER_API_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"

# Ensure Database Exists
def create_database():
    """Ensure that the database exists."""
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"]
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS weather_db")
    cursor.close()
    conn.close()

# Ensure Tables Exist
def create_tables():
    """Create `current`, `hourly`, and `daily` weather tables."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS current (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lat FLOAT NOT NULL,
            lon FLOAT NOT NULL,
            timezone VARCHAR(50),
            timezone_offset INT,
            dt DATETIME NOT NULL,
            sunrise DATETIME NOT NULL,
            sunset DATETIME NOT NULL,
            temp FLOAT NOT NULL,
            feels_like FLOAT NOT NULL,
            pressure INT NOT NULL,
            humidity INT NOT NULL,
            dew_point FLOAT NOT NULL,
            uvi FLOAT DEFAULT 0.0,
            clouds INT NOT NULL,
            visibility INT DEFAULT 10000,
            wind_speed FLOAT NOT NULL,
            wind_deg INT NOT NULL,
            wind_gust FLOAT DEFAULT NULL,
            weather_id INT NOT NULL,
            weather_main VARCHAR(50),
            weather_desc VARCHAR(100),
            weather_icon VARCHAR(10)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hourly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            dt DATETIME NOT NULL,
            temp FLOAT NOT NULL,
            feels_like FLOAT NOT NULL,
            pressure INT NOT NULL,
            humidity INT NOT NULL,
            wind_speed FLOAT NOT NULL,
            wind_deg INT NOT NULL,
            wind_gust FLOAT DEFAULT NULL,
            clouds INT NOT NULL,
            pop FLOAT NOT NULL,
            weather_id INT NOT NULL,
            weather_main VARCHAR(50),
            weather_desc VARCHAR(100),
            weather_icon VARCHAR(10)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily (
            id INT AUTO_INCREMENT PRIMARY KEY,
            dt DATETIME NOT NULL,
            sunrise DATETIME NOT NULL,
            sunset DATETIME NOT NULL,
            moonrise DATETIME NOT NULL,
            moonset DATETIME NOT NULL,
            moon_phase FLOAT NOT NULL,
            temp_day FLOAT NOT NULL,
            temp_min FLOAT NOT NULL,
            temp_max FLOAT NOT NULL,
            temp_night FLOAT NOT NULL,
            temp_eve FLOAT NOT NULL,
            temp_morn FLOAT NOT NULL,
            pressure INT NOT NULL,
            humidity INT NOT NULL,
            wind_speed FLOAT NOT NULL,
            wind_deg INT NOT NULL,
            wind_gust FLOAT DEFAULT NULL,
            clouds INT NOT NULL,
            uvi FLOAT DEFAULT 0.0,
            pop FLOAT NOT NULL,
            rain FLOAT DEFAULT 0.0,
            weather_id INT NOT NULL,
            weather_main VARCHAR(50),
            weather_desc VARCHAR(100),
            weather_icon VARCHAR(10)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print(" Database tables checked/created successfully!")

# Function to Insert Data into MySQL
def save_to_mysql(table, data):
    """Generic MySQL data insertion function."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = None

        if table == "current":
            sql = """INSERT INTO current 
            (lat, lon, timezone, timezone_offset, dt, sunrise, sunset, temp, feels_like, pressure, humidity, dew_point, 
            uvi, clouds, visibility, wind_speed, wind_deg, wind_gust, weather_id, weather_main, weather_desc, weather_icon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        elif table == "hourly":
            sql = """INSERT INTO hourly
            (dt, temp, feels_like, pressure, humidity, wind_speed, wind_deg, wind_gust, clouds, pop, weather_id, 
            weather_main, weather_desc, weather_icon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        elif table == "daily":
            sql = """INSERT INTO daily
            (dt, sunrise, sunset, moonrise, moonset, moon_phase, temp_day, temp_min, temp_max, temp_night, temp_eve, 
            temp_morn, pressure, humidity, wind_speed, wind_deg, wind_gust, clouds, uvi, pop, rain, weather_id, 
            weather_main, weather_desc, weather_icon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        cursor.execute(sql, data)
        conn.commit()

    except mysql.connector.Error as err:
        print(f" MySQL Error: {err}")

    finally:
        cursor.close()
        conn.close()
        print(f" Data inserted into {table} table successfully!")

# Extract Functions
def extract_current(data):
    """Extracts 'current' weather data."""
    current = data["current"]
    return (
        data["lat"], data["lon"], data["timezone"], data["timezone_offset"],
        datetime.utcfromtimestamp(current["dt"]),
        datetime.utcfromtimestamp(current["sunrise"]),
        datetime.utcfromtimestamp(current["sunset"]),
        current["temp"], current["feels_like"], current["pressure"], current["humidity"],
        current["dew_point"], current.get("uvi", 0.0), current["clouds"], current.get("visibility", 10000),
        current["wind_speed"], current["wind_deg"], current.get("wind_gust", None),
        current["weather"][0]["id"], current["weather"][0]["main"], current["weather"][0]["description"],
        current["weather"][0]["icon"]
    )

def extract_hourly(hour):
    """Extracts 'hourly' weather data."""
    return (
        datetime.utcfromtimestamp(hour["dt"]),
        hour["temp"], hour["feels_like"], hour["pressure"], hour["humidity"],
        hour["wind_speed"], hour["wind_deg"], hour.get("wind_gust"),
        hour["clouds"], hour["pop"], 
        hour["weather"][0]["id"], hour["weather"][0]["main"],
        hour["weather"][0]["description"], hour["weather"][0]["icon"]
    )

def extract_daily(day):
    """Extracts 'daily' weather data."""
    return (
        datetime.utcfromtimestamp(day["dt"]),
        datetime.utcfromtimestamp(day["sunrise"]),
        datetime.utcfromtimestamp(day["sunset"]),
        datetime.utcfromtimestamp(day["moonrise"]),
        datetime.utcfromtimestamp(day["moonset"]),
        day["moon_phase"], day["temp"]["day"], day["temp"]["min"], day["temp"]["max"],
        day["temp"]["night"], day["temp"]["eve"], day["temp"]["morn"],
        day["pressure"], day["humidity"], day["wind_speed"], day["wind_deg"],
        day.get("wind_gust"), day["clouds"], day["pop"], day.get("rain", 0.0),
        day["weather"][0]["id"], day["weather"][0]["main"],
        day["weather"][0]["description"], day["weather"][0]["icon"]
    )

# Fetch & Save Weather Data
def get_weather():
    """Fetch and save weather data."""
    response = requests.get(WEATHER_API_URL)
    if response.status_code == 200:
        data = response.json()
        save_to_mysql("current", extract_current(data))
        for hour in data["hourly"][:24]:
            save_to_mysql("hourly", extract_hourly(hour))
        for day in data["daily"][:8]:
            save_to_mysql("daily", extract_daily(day))

if __name__ == "__main__":
    print(" Weather script started!")  # Debugging output
    create_database()
    create_tables()
    
    print(" Fetching weather data...")
    get_weather()

    print(" Weather data fetched and stored!")
