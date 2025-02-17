import requests
import time
import schedule

API_KEY = "ef3732293c7375506846347d15ce27b4"  
CITY = "Dublin"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

def get_weather():
    """Fetch Dublin weather and save it locally"""
    try:
        response = requests.get(URL, timeout=10)  
        response.raise_for_status()  
        data = response.json()

        temp = data["main"]["temp"]
        weather = data["weather"][0]["description"]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        weather_data = f"{timestamp}, {temp}°C, {weather}\n"
        with open("weather_log.txt", "a") as file:
            file.write(weather_data)
        
        print("Weather data saved:", weather_data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")

schedule.every(1).hours.do(get_weather)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nScript stopped by user. Exiting gracefully.")
