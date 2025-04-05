import requests
import os
from datetime import datetime
from sqlalchemy import text
from config import Config
from dotenv import load_dotenv
from app.models.db import engine

# Load environment variables
load_dotenv()
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT = os.getenv("WEATHER_LAT", "53.350140")
LON = os.getenv("WEATHER_LON", "-6.266155")
WEATHER_API_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={WEATHER_API_KEY}&units=metric"

print(" Loaded API Key:", WEATHER_API_KEY)

# Insert helpers
def insert_current(data, conn):
    conn.execute(text("DELETE FROM current"))
    conn.execute(text("""
        INSERT INTO current (lat, lon, timezone, timezone_offset, dt, sunrise, sunset, temp, feels_like, pressure, humidity, dew_point, 
            uvi, clouds, visibility, wind_speed, wind_deg, wind_gust, weather_id, weather_main, weather_desc, weather_icon)
        VALUES (:lat, :lon, :timezone, :timezone_offset, :dt, :sunrise, :sunset, :temp, :feels_like, :pressure, :humidity, :dew_point, 
            :uvi, :clouds, :visibility, :wind_speed, :wind_deg, :wind_gust, :weather_id, :weather_main, :weather_desc, :weather_icon)
    """), {
        "lat": data["lat"],
        "lon": data["lon"],
        "timezone": data["timezone"],
        "timezone_offset": data["timezone_offset"],
        "dt": datetime.fromtimestamp(data["current"]["dt"]),
        "sunrise": datetime.fromtimestamp(data["current"]["sunrise"]),
        "sunset": datetime.fromtimestamp(data["current"]["sunset"]),
        "temp": data["current"]["temp"],
        "feels_like": data["current"]["feels_like"],
        "pressure": data["current"]["pressure"],
        "humidity": data["current"]["humidity"],
        "dew_point": data["current"]["dew_point"],
        "uvi": data["current"].get("uvi", 0.0),
        "clouds": data["current"]["clouds"],
        "visibility": data["current"].get("visibility", 10000),
        "wind_speed": data["current"]["wind_speed"],
        "wind_deg": data["current"]["wind_deg"],
        "wind_gust": data["current"].get("wind_gust"),
        "weather_id": data["current"]["weather"][0]["id"],
        "weather_main": data["current"]["weather"][0]["main"],
        "weather_desc": data["current"]["weather"][0]["description"],
        "weather_icon": data["current"]["weather"][0]["icon"]
    })

def insert_hourly(data, conn):
    conn.execute(text("DELETE FROM hourly"))
    hourly_data = []
    for h in data["hourly"][:24]:
        hourly_data.append({
            "lat": data["lat"],
            "lon": data["lon"],
            "timezone": data["timezone"],
            "timezone_offset": data["timezone_offset"],
            "dt": datetime.fromtimestamp(h["dt"]),
            "temp": h["temp"],
            "feels_like": h["feels_like"],
            "pressure": h["pressure"],
            "humidity": h["humidity"],
            "dew_point": h["dew_point"],
            "uvi": h.get("uvi", 0.0),
            "clouds": h["clouds"],
            "visibility": h.get("visibility", 10000),
            "wind_speed": h["wind_speed"],
            "wind_deg": h["wind_deg"],
            "wind_gust": h.get("wind_gust"),
            "weather_id": h["weather"][0]["id"],
            "weather_main": h["weather"][0]["main"],
            "weather_desc": h["weather"][0]["description"],
            "weather_icon": h["weather"][0]["icon"],
            "pop": h["pop"]
        })
    conn.executemany(text("""
        INSERT INTO hourly (lat, lon, timezone, timezone_offset, dt, temp, feels_like, pressure, humidity, dew_point,
            uvi, clouds, visibility, wind_speed, wind_deg, wind_gust, weather_id, weather_main, weather_desc, weather_icon, pop)
        VALUES (:lat, :lon, :timezone, :timezone_offset, :dt, :temp, :feels_like, :pressure, :humidity, :dew_point,
            :uvi, :clouds, :visibility, :wind_speed, :wind_deg, :wind_gust, :weather_id, :weather_main, :weather_desc, :weather_icon, :pop)
    """), hourly_data)

def insert_daily(data, conn):
    conn.execute(text("DELETE FROM daily"))
    daily_data = []
    for d in data["daily"][:8]:
        daily_data.append({
            "lat": data["lat"],
            "lon": data["lon"],
            "timezone": data["timezone"],
            "timezone_offset": data["timezone_offset"],
            "dt": datetime.fromtimestamp(d["dt"]),
            "sunrise": datetime.fromtimestamp(d["sunrise"]),
            "sunset": datetime.fromtimestamp(d["sunset"]),
            "moonrise": datetime.fromtimestamp(d["moonrise"]),
            "moonset": datetime.fromtimestamp(d["moonset"]),
            "moon_phase": d["moon_phase"],
            "summary": None,
            "temp_day": d["temp"]["day"],
            "temp_min": d["temp"]["min"],
            "temp_max": d["temp"]["max"],
            "temp_night": d["temp"]["night"],
            "temp_eve": d["temp"]["eve"],
            "temp_morn": d["temp"]["morn"],
            "feels_like_day": d["feels_like"]["day"],
            "feels_like_night": d["feels_like"]["night"],
            "feels_like_eve": d["feels_like"]["eve"],
            "feels_like_morn": d["feels_like"]["morn"],
            "pressure": d["pressure"],
            "humidity": d["humidity"],
            "dew_point": d["dew_point"],
            "wind_speed": d["wind_speed"],
            "wind_deg": d["wind_deg"],
            "wind_gust": d.get("wind_gust"),
            "clouds": d["clouds"],
            "uvi": d.get("uvi", 0.0),
            "pop": d["pop"],
            "rain": d.get("rain", 0.0),
            "weather_id": d["weather"][0]["id"],
            "weather_main": d["weather"][0]["main"],
            "weather_desc": d["weather"][0]["description"],
            "weather_icon": d["weather"][0]["icon"]
        })
    conn.executemany(text("""
        INSERT INTO daily (lat, lon, timezone, timezone_offset, dt, sunrise, sunset, moonrise, moonset, moon_phase,
            summary, temp_day, temp_min, temp_max, temp_night, temp_eve, temp_morn, feels_like_day, feels_like_night,
            feels_like_eve, feels_like_morn, pressure, humidity, dew_point, wind_speed, wind_deg, wind_gust, clouds,
            uvi, pop, rain, weather_id, weather_main, weather_desc, weather_icon)
        VALUES (:lat, :lon, :timezone, :timezone_offset, :dt, :sunrise, :sunset, :moonrise, :moonset, :moon_phase,
            :summary, :temp_day, :temp_min, :temp_max, :temp_night, :temp_eve, :temp_morn, :feels_like_day, :feels_like_night,
            :feels_like_eve, :feels_like_morn, :pressure, :humidity, :dew_point, :wind_speed, :wind_deg, :wind_gust, :clouds,
            :uvi, :pop, :rain, :weather_id, :weather_main, :weather_desc, :weather_icon)
    """), daily_data)

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
        try:
            insert_current(data, conn)
            insert_hourly(data, conn)
            insert_daily(data, conn)
            transaction.commit()
            print("Weather data saved successfully!")
        except Exception as e:
            transaction.rollback()
            print(f"Failed to save weather data: {e}")