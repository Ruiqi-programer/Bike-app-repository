import requests
import mysql.connector
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
URL = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

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
            dt TIMESTAMP NOT NULL PRIMARY KEY, 
            feels_like FLOAT, 
            humidity INT, 
            pressure INT, 
            sunrise TIMESTAMP, 
            sunset TIMESTAMP, 
            temp FLOAT, 
            uvi FLOAT, 
            weather_id INT, 
            wind_gust FLOAT, 
            wind_speed FLOAT, 
            rain_1h FLOAT, 
            snow_1h FLOAT
        )
    """)

    # Create `daily` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily (
            dt TIMESTAMP NOT NULL, 
            future_dt TIMESTAMP NOT NULL, 
            humidity INT, 
            pop FLOAT, 
            pressure INT, 
            temp_max FLOAT, 
            temp_min FLOAT, 
            uvi FLOAT, 
            weather_id INT, 
            wind_speed FLOAT, 
            wind_gust FLOAT, 
            rain FLOAT, 
            snow FLOAT, 
            PRIMARY KEY (dt, future_dt)
        )
    """)

    # Create `hourly` table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hourly (
            dt TIMESTAMP NOT NULL, 
            future_dt TIMESTAMP NOT NULL, 
            feels_like FLOAT, 
            humidity INT, 
            pop FLOAT, 
            pressure INT, 
            temp FLOAT, 
            uvi FLOAT, 
            weather_id INT, 
            wind_speed FLOAT, 
            wind_gust FLOAT, 
            rain_1h FLOAT, 
            snow_1h FLOAT, 
            PRIMARY KEY (dt, future_dt)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database tables checked/created successfully!")

def save_to_mysql(table, data):
    """Generic MySQL data insertion function."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        if table == "current":
            sql = """INSERT INTO current 
                     (dt, feels_like, humidity, pressure, sunrise, sunset, temp, weather_id, wind_speed, wind_gust, rain_1h, snow_1h) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                     ON DUPLICATE KEY UPDATE temp=VALUES(temp), feels_like=VALUES(feels_like), humidity=VALUES(humidity)"""
            cursor.execute(sql, data)
        
        elif table == "daily":
            sql = """INSERT INTO daily 
                     (dt, future_dt, humidity, pop, pressure, temp_max, temp_min, uvi, weather_id, wind_speed, wind_gust, rain, snow) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                     ON DUPLICATE KEY UPDATE temp_max=VALUES(temp_max), temp_min=VALUES(temp_min), uvi=VALUES(uvi)"""
            cursor.execute(sql, data)

        elif table == "hourly":
            sql = """INSERT INTO hourly 
                     (dt, future_dt, feels_like, humidity, pop, pressure, temp, uvi, weather_id, wind_speed, wind_gust, rain_1h, snow_1h) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                     ON DUPLICATE KEY UPDATE temp=VALUES(temp), feels_like=VALUES(feels_like), humidity=VALUES(humidity)"""
            cursor.execute(sql, data)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"Data inserted into {table} table successfully!")

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")

def get_weather():
    """Fetch weather data and store it in MySQL."""
    response = requests.get(URL)
    data = response.json()

    if response.status_code == 200:
        dt = datetime.utcfromtimestamp(data["dt"])
        sunrise = datetime.utcfromtimestamp(data["sys"]["sunrise"])
        sunset = datetime.utcfromtimestamp(data["sys"]["sunset"])

        weather_id = data["weather"][0]["id"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        temp = data["main"]["temp"]
        wind_speed = data["wind"]["speed"]
        wind_gust = data["wind"].get("gust", None)
        rain_1h = data.get("rain", {}).get("1h", None)
        snow_1h = data.get("snow", {}).get("1h", None)

        current_data = (dt, feels_like, humidity, pressure, sunrise, sunset, temp, weather_id, wind_speed, wind_gust, rain_1h, snow_1h)
        save_to_mysql("current", current_data)

        if "daily" in data:
            for daily in data["daily"]:
                future_dt = datetime.utcfromtimestamp(daily["dt"])
                humidity = daily["humidity"]
                pop = daily["pop"]
                pressure = daily["pressure"]
                temp_max = daily["temp"]["max"]
                temp_min = daily["temp"]["min"]
                uvi = daily["uvi"]
                weather_id = daily["weather"][0]["id"]
                wind_speed = daily["wind_speed"]
                wind_gust = daily.get("wind_gust", None)
                rain = daily.get("rain", None)
                snow = daily.get("snow", None)

                daily_data = (dt, future_dt, humidity, pop, pressure, temp_max, temp_min, uvi, weather_id, wind_speed, wind_gust, rain, snow)
                save_to_mysql("daily", daily_data)

        if "hourly" in data:
            for hourly in data["hourly"]:
                future_dt = datetime.utcfromtimestamp(hourly["dt"])
                feels_like = hourly["feels_like"]
                humidity = hourly["humidity"]
                pop = hourly["pop"]
                pressure = hourly["pressure"]
                temp = hourly["temp"]
                uvi = hourly.get("uvi", 0)
                weather_id = hourly["weather"][0]["id"]
                wind_speed = hourly["wind_speed"]
                wind_gust = hourly.get("wind_gust", None)
                rain_1h = hourly.get("rain", {}).get("1h", None)
                snow_1h = hourly.get("snow", {}).get("1h", None)

                hourly_data = (dt, future_dt, feels_like, humidity, pop, pressure, temp, uvi, weather_id, wind_speed, wind_gust, rain_1h, snow_1h)
                save_to_mysql("hourly", hourly_data)

    else:
        print(" Failed to retrieve weather data:", data)

# Run the program
create_database()
create_tables()
get_weather()

