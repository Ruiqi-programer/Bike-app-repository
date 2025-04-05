from flask import Blueprint, jsonify, render_template
from sqlalchemy import text
from app.models.db import engine
import os

main = Blueprint('main', __name__)

@main.route("/")
def index():
    return render_template("index.html", google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY"))

@main.route("/api/weather", methods=["GET"])
def weather():
    try:
        with engine.connect() as connection:
            # Current weather
            current_result = connection.execute(text("""
                SELECT dt, temp, feels_like, humidity, wind_speed, clouds
                FROM current
                ORDER BY dt DESC
                LIMIT 1;
            """)).mappings().first()

            # Next 12 hours
            hourly_result = connection.execute(text("""
                SELECT dt, temp, feels_like, humidity, wind_speed, clouds, pop
                FROM hourly
                WHERE dt >= NOW()
                ORDER BY dt ASC
                LIMIT 12;
            """)).mappings().all()

            # Next 8 days
            daily_result = connection.execute(text("""
                SELECT dt, temp_day, temp_min, temp_max, humidity, wind_speed, clouds, pop, weather_desc, weather_icon
                FROM daily
                ORDER BY dt ASC
                LIMIT 8;
            """)).mappings().all()

        return jsonify({
            "current": dict(current_result) if current_result else {},
            "hourly": [dict(row) for row in hourly_result],
            "daily": [dict(row) for row in daily_result]
        })

    except Exception as e:
        print("❌ Weather DB error:", e)
        return jsonify({"error": "Could not fetch weather"}), 500

@main.route("/api/stations", methods=["GET"])
def stations():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT s.station_id, s.name, s.latitude, s.longitude, s.total_bike_stands,
                       ss.available_bikes, ss.available_bike_stands
                FROM stations s
                JOIN (
                    SELECT station_id, available_bikes, available_bike_stands
                    FROM station_status
                    WHERE (station_id, last_update) IN (
                        SELECT station_id, MAX(last_update)
                        FROM station_status
                        GROUP BY station_id
                    )
                ) ss ON s.station_id = ss.station_id;
            """)).mappings().all()

        return jsonify([dict(row) for row in result])

    except Exception as e:
        print("❌ Station DB error:", e)
        return jsonify({"error": "Could not fetch stations"}), 500