
import os
import joblib
from sqlalchemy import text
from config import Config
import requests
from datetime import datetime
import pandas as pd

_model = None  

def load_model():
    """
    Load the trained machine learning model if not already loaded.
    Returns:
        The loaded model.
    """
    global _model
    if _model is None:
        model_path = os.path.join(os.path.dirname(__file__), "bike_availability_model.pkl")
        _model = joblib.load(model_path)
    return _model


def fetch_weather_forecast(date_time):
    try:
        response = requests.get(Config.WEATHER_API_URL)
        if response.status_code != 200:
            raise Exception("OpenWeather API error")

        weather_data = response.json()
        forecast = min(
            weather_data["hourly"],
            key=lambda x: abs(datetime.fromtimestamp(x["dt"]) - date_time)
        )

        return {
            "temperature": forecast["temp"],
            "humidity": forecast["humidity"],
            "wind_speed": forecast["wind_speed"],
            "precipitation": forecast.get("pop", 0.0),
            "pressure": forecast["pressure"]
        }

    except Exception as e:
        print("⚠️ Weather fetch error:", e)
        # fallback default weather
        return {"temperature": 15.0,
            "humidity": 70.0,
            "wind_speed": 5.0,
            "precipitation": 0.0,
            "pressure": 1012.0}


def predict(station_id, date, time):
    try:
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        weather = fetch_weather_forecast(dt)

        features_dict = {
            "station_id": int(station_id),
            "max_air_temperature_celsius": weather["temperature"],
            "max_relative_humidity_percent": weather["humidity"],
            "max_barometric_pressure_hpa": weather["pressure"],
            "wind_speed": weather["wind_speed"],
            "precipitation": weather["precipitation"],
            "hour": dt.hour,
            "day_of_week": dt.weekday()
        }

        features_df = pd.DataFrame([features_dict])
        model = load_model()
        prediction = model.predict(features_df)[0]
        return round(prediction)

    except Exception as e:
        return {"error": str(e)}