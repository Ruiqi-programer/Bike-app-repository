import requests
import time
import schedule
import json

API_KEY = "ef3732293c7375506846347d15ce27b4"
LAT = 53.350140  # Dublin latitude
LON = -6.266155  # Dublin longitude
URL = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

def get_weather():
    """Fetch Dublin weather using latitude & longitude and save all details locally"""
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Collect all data
        weather_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "coordinates": data["coord"],
            "weather": data["weather"],
            "base": data["base"],
            "main": data["main"],
            "visibility": data.get("visibility", "N/A"),
            "wind": data["wind"],
            "clouds": data["clouds"],
            "dt": data["dt"],
            "sys": data["sys"],
            "timezone": data["timezone"],
            "id": data["id"],
            "name": data["name"],
            "cod": data["cod"]
        }

        # Save to file
        with open("weather_log.json", "a", encoding="utf-8") as file:
            file.write(json.dumps(weather_data, indent=4) + ",\n")

        print("Weather data saved:", weather_data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")

# Schedule to run every 1 hour
schedule.every(1).hours.do(get_weather)

# Graceful exit on user interruption
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nScript stopped by user. Exiting gracefully.")

