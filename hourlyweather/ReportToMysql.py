import requests
import mysql.connector
import time
from datetime import datetime

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "grq990823",
    "port": "3306",
    "database": "weather_db"
}

# API Information
API_KEY = "ef3732293c7375506846347d15ce27b4"
LAT = 53.350140  # Dublin latitude
LON = -6.266155  # Dublin longitude
URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,alerts&appid={API_KEY}"

def create_database():
    """Ensure that the database exists."""
    conn = mysql.connector.connect(host=DB_CONFIG["host"], user=DB_CONFIG["user"], password=DB_CONFIG["password"], port=DB_CONFIG["port"])
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS weather_db")
    cursor.close()
    conn.close()

def create_tables():
    """Create the necessary database tables."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Create `current` table
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

    # Create `daily` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lat FLOAT NOT NULL,
            lon FLOAT NOT NULL,
            timezone VARCHAR(50),
            timezone_offset INT,
            dt DATETIME NOT NULL,
            sunrise DATETIME NOT NULL,
            sunset DATETIME NOT NULL,
            moonrise DATETIME NOT NULL,
            moonset DATETIME NOT NULL,
            moon_phase FLOAT NOT NULL,
            summary TEXT,
            temp_day FLOAT NOT NULL,
            temp_min FLOAT NOT NULL,
            temp_max FLOAT NOT NULL,
            temp_night FLOAT NOT NULL,
            temp_eve FLOAT NOT NULL,
            temp_morn FLOAT NOT NULL,
            feels_like_day FLOAT NOT NULL,
            feels_like_night FLOAT NOT NULL,
            feels_like_eve FLOAT NOT NULL,
            feels_like_morn FLOAT NOT NULL,
            pressure INT NOT NULL,
            humidity INT NOT NULL,
            dew_point FLOAT NOT NULL,
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

    # Create `hourly` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hourly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lat FLOAT NOT NULL,
            lon FLOAT NOT NULL,
            timezone VARCHAR(50),
            timezone_offset INT,
            dt DATETIME NOT NULL,
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
            weather_icon VARCHAR(10),
            pop FLOAT NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database tables checked/created successfully!")

def save_to_mysql(table, data):
    """Generic MySQL data insertion function."""
    try:
        sql = None
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        if table == "current":
                sql = """INSERT INTO current 
                (lat, lon, timezone, timezone_offset, dt, sunrise, sunset, temp, feels_like, pressure, humidity, dew_point, 
                uvi, clouds, visibility, wind_speed, wind_deg, wind_gust, weather_id, weather_main, weather_desc, weather_icon)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
        elif table == "hourly":
                sql = """INSERT INTO hourly
                (lat, lon, timezone, timezone_offset, dt, temp, feels_like, pressure, humidity, dew_point, uvi, clouds, visibility, 
                wind_speed, wind_deg, wind_gust, weather_id, weather_main, weather_desc, weather_icon, pop)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
        elif table == "daily":
                sql = """INSERT INTO daily
                (lat, lon, timezone, timezone_offset, dt, sunrise, sunset, moonrise, moonset, moon_phase, summary, temp_day, 
                temp_min, temp_max, temp_night, temp_eve, temp_morn, feels_like_day, feels_like_night, feels_like_eve, 
                feels_like_morn, pressure, humidity, dew_point, wind_speed, wind_deg, wind_gust, clouds, uvi, pop, rain, 
                weather_id, weather_main, weather_desc, weather_icon)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        if sql is None: 
            print(f"Error: Invalid table name '{table}'")
            return

        cursor.execute(sql, data)
        conn.commit()
    
    except mysql.connector.Error as err:
        print(f"MySQL Error.")

    finally :
        cursor.close()
        conn.close()
        print(f"Data inserted into {table} table successfully!")


def get_weather():
    """Fetch weather data and store it in MySQL."""
    response = requests.get(URL)

    #if response.status_code != 200:
        #print("Failed to retrieve weather data:", response.text)
        #return

    data = response.json()
    lat, lon, timezone, timezone_offset = data["lat"], data["lon"], data["timezone"], data["timezone_offset"]

    current = data["current"]
    current_data = (
        lat, lon, timezone, timezone_offset,
        datetime.utcfromtimestamp(current["dt"]),
        datetime.utcfromtimestamp(current["sunrise"]),
        datetime.utcfromtimestamp(current["sunset"]),
        current["temp"], current["feels_like"], current["pressure"], current["humidity"],
        current["dew_point"], current.get("uvi", 0.0), current["clouds"], current.get("visibility", 10000),
        current["wind_speed"], current["wind_deg"], current.get("wind_gust", None),
        current["weather"][0]["id"], current["weather"][0]["main"], current["weather"][0]["description"], current["weather"][0]["icon"]
    )
    save_to_mysql("current", current_data)

    for daily in data.get("daily", []): 
        weather = daily.get("weather", [{}])  
        daily_data = (
            lat, lon, timezone, timezone_offset,
            datetime.utcfromtimestamp(daily["dt"]),
            datetime.utcfromtimestamp(daily["sunrise"]),
            datetime.utcfromtimestamp(daily["sunset"]),
            datetime.utcfromtimestamp(daily.get("moonrise", 0)), 
            datetime.utcfromtimestamp(daily.get("moonset", 0)),   
            daily["moon_phase"],
            daily.get("summary", "No summary available"), 
            daily["temp"]["day"], daily["temp"]["min"], daily["temp"]["max"],
            daily["temp"]["night"], daily["temp"]["eve"], daily["temp"]["morn"],
            daily["feels_like"]["day"], daily["feels_like"]["night"],
            daily["feels_like"]["eve"], daily["feels_like"]["morn"],
            daily["pressure"], daily["humidity"], daily["dew_point"],
            daily["wind_speed"], daily["wind_deg"],
            daily.get("wind_gust", 0), 
            daily["clouds"], daily.get("uvi", 0.0), 
            daily["pop"], daily.get("rain", 0),
            weather[0].get("id", 0), weather[0].get("main", "Unknown"),
            weather[0].get("description", "Unknown"), weather[0].get("icon", "01d")
        )
        
        save_to_mysql("daily", daily_data)


    for hourly in data.get("hourly", []):
        hourly_data = (
            lat, lon, timezone, timezone_offset,
            datetime.utcfromtimestamp(hourly["dt"]),
            hourly["temp"], hourly["feels_like"], hourly["pressure"], hourly["humidity"],
            hourly["dew_point"], hourly.get("uvi", 0.0), hourly["clouds"], hourly.get("visibility", 10000),
            hourly["wind_speed"], hourly["wind_deg"], hourly.get("wind_gust", None),
            hourly["weather"][0]["id"], hourly["weather"][0]["main"], hourly["weather"][0]["description"], hourly["weather"][0]["icon"],
            hourly["pop"]
        )
        save_to_mysql("hourly", hourly_data)
        
    #else:
        #print("Failed to retrieve weather data:", data)

if __name__ == "__main__":
    create_database()
    create_tables()
    
    while True:
        get_weather()
        print("Weather data fetched and stored. Sleeping for 1 hour...\n")
        time.sleep(3600)


