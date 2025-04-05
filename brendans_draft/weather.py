import requests
import mysql.connector
import os
import json
from datetime import datetime
from config import DB_CONFIG
from dotenv import load_dotenv
from db import engine  # Import database engine

# Load environment variables
load_dotenv()
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT = os.getenv("WEATHER_LAT", "53.350140")
LON = os.getenv("WEATHER_LON", "-6.266155")
WEATHER_API_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"

print(" Loaded API Key:", WEATHER_API_KEY)

# Insert helpers
def insert_current(data, conn):
    conn.execute("DELETE * FROM current")
    conn.execute("""
        INSERT INTO current (lat, lon, timezone, timezone_offset, dt, sunrise, sunset, temp, feels_like, pressure, humidity, dew_point, 
            uvi, clouds, visibility, wind_speed, wind_deg, wind_gust, weather_id, weather_main, weather_desc, weather_icon)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["lat"], data["lon"], data["timezone"], data["timezone_offset"],
        datetime.fromtimestamp(data["current"]["dt"]),
        datetime.fromtimestamp(data["current"]["sunrise"]),
        datetime.fromtimestamp(data["current"]["sunset"]),
        data["current"]["temp"], data["current"]["feels_like"], data["current"]["pressure"],
        data["current"]["humidity"], data["current"]["dew_point"], data["current"].get("uvi", 0.0),
        data["current"]["clouds"], data["current"].get("visibility", 10000),
        data["current"]["wind_speed"], data["current"]["wind_deg"], data["current"].get("wind_gust"),
        data["current"]["weather"][0]["id"], data["current"]["weather"][0]["main"],
        data["current"]["weather"][0]["description"], data["current"]["weather"][0]["icon"]
    ))

def insert_hourly(data, conn):
    conn.execute("DELETE * FROM hourly")
    hourly_data = []
    for h in data["hourly"][:24]:
        hourly_data.append((
            data["lat"], data["lon"], data["timezone"], data["timezone_offset"],
            datetime.fromtimestamp(h["dt"]), h["temp"], h["feels_like"], h["pressure"], h["humidity"],
            h["dew_point"], h.get("uvi", 0.0), h["clouds"], h.get("visibility", 10000), h["wind_speed"], h["wind_deg"],
            h.get("wind_gust"), h["weather"][0]["id"], h["weather"][0]["main"],
            h["weather"][0]["description"], h["weather"][0]["icon"], h["pop"]
        ))
    conn.executemany("""
        INSERT INTO hourly (lat, lon, timezone, timezone_offset, dt, temp, feels_like, pressure, humidity, dew_point,
            uvi, clouds, visibility, wind_speed, wind_deg, wind_gust, weather_id, weather_main, weather_desc, weather_icon, pop)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, hourly_data)

def insert_daily(data, conn):
    conn.execute("DELETE * FROM daily")
    daily_data = []
    for d in data["daily"][:8]:
        daily_data.append((
            data["lat"], data["lon"], data["timezone"], data["timezone_offset"],
            datetime.fromtimestamp(d["dt"]), datetime.fromtimestamp(d["sunrise"]), datetime.fromtimestamp(d["sunset"]),
            datetime.fromtimestamp(d["moonrise"]), datetime.fromtimestamp(d["moonset"]), d["moon_phase"],
            None,  # summary
            d["temp"]["day"], d["temp"]["min"], d["temp"]["max"], d["temp"]["night"],
            d["temp"]["eve"], d["temp"]["morn"], d["feels_like"]["day"], d["feels_like"]["night"],
            d["feels_like"]["eve"], d["feels_like"]["morn"],
            d["pressure"], d["humidity"], d["dew_point"],
            d["wind_speed"], d["wind_deg"], d.get("wind_gust"), d["clouds"], d.get("uvi", 0.0), d["pop"],
            d.get("rain", 0.0), d["weather"][0]["id"], d["weather"][0]["main"],
            d["weather"][0]["description"], d["weather"][0]["icon"]
        ))
    conn.executemany("""
        INSERT INTO daily (lat, lon, timezone, timezone_offset, dt, sunrise, sunset, moonrise, moonset, moon_phase,
            summary, temp_day, temp_min, temp_max, temp_night, temp_eve, temp_morn, feels_like_day, feels_like_night,
            feels_like_eve, feels_like_morn, pressure, humidity, dew_point, wind_speed, wind_deg, wind_gust, clouds,
            uvi, pop, rain, weather_id, weather_main, weather_desc, weather_icon)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s)
    """, daily_data)

def fetch_weather():
    print(" Fetching from OpenWeather API...")
    response = requests.get(WEATHER_API_URL)
    print(" Response status:", response.status_code)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch weather data")
        return None

def update_weather():
    print(" Weather update script started")
    data = fetch_weather()
    if not data:
        return

    with engine.connect() as conn:
        transaction = conn.begin()
        insert_current(data, conn)
        insert_hourly(data, conn)
        insert_daily(data, conn)
        transaction.commit()
        print("Weather data saved successfully!")

if __name__ == "__main__":
    update_weather()