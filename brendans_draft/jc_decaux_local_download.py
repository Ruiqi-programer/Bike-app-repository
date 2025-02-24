import requests
import json
import time
from config import BIKE_API_URL, WEATHER_API_URL

def save_json(filename, data):
    """Save API data to a local JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def fetch_bike_data():
    """Fetch and save bike station data."""
    response = requests.get(BIKE_API_URL, timeout=10)
    if response.status_code == 200:
        save_json("bike_data.json", response.json())
        print(" Bike data saved successfully.")
    else:
        print(f" Failed to fetch bike data: {response.status_code}")

def fetch_weather_data():
    """Fetch and save weather data."""
    response = requests.get(WEATHER_API_URL, timeout=10)
    if response.status_code == 200:
        save_json("weather_data.json", response.json())
        print(" Weather data saved successfully.")
    else:
        print(f" Failed to fetch weather data: {response.status_code}")

# Run the scraping every 5 minutes for bikes and every hour for weather
while True:
    fetch_bike_data()
    if int(time.time()) % 3600 == 0:
        fetch_weather_data()
    time.sleep(300)  # 5 minutes
