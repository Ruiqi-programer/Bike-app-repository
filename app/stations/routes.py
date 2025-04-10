from flask import Blueprint, jsonify, request,render_template
from sqlalchemy import text
from app.models.db import engine
from config import Config
import os
import pandas as pd
from app.models.model_utils import predict
from datetime import datetime


stations = Blueprint('stations', __name__, template_folder='templates', static_folder='static')


@stations.route("/map")
def map():
    return render_template("stations.html",google_maps_api_key=Config.GOOGLE_MAPS_API_KEY)


@stations.route("/api/weather", methods=["GET"])
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

@stations.route("/api/stations", methods=["GET"])
def api_stations():
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
    

@stations.route("/predict", methods=["GET"])
def predict_route():
    try:
        date = request.args.get("date")
        time = request.args.get("time")
        station_id = request.args.get("station_id")

        if not all([date, time, station_id]):
            return jsonify({"error": "Missing date, time, or station_id"}), 400

        result = predict(station_id, date, time)
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 500
        return jsonify({"predicted_available_bikes": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stations.route("/predict_range", methods=["GET"])
def predict_range():
    try:
        date = request.args.get("date")
        time = request.args.get("time")
        station_id = request.args.get("station_id")

        if not all([date, time, station_id]):
            return jsonify({"error": "Missing date, time, or station_id"}), 400

        result = predict(station_id, date, time)
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 500
        return jsonify({"predicted_available_bikes": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
