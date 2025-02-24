from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DB_CONFIG

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Database connection using SQLAlchemy
connection_string = f"mysql+mysqldb://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string, echo=True)

def get_stations():
    """Fetch bike station data including availability from MySQL."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT s.station_id, s.name, s.latitude, s.longitude, s.total_bike_stands,
                       ss.available_bikes, ss.available_bike_stands
                FROM stations s
                JOIN station_status ss ON s.station_id = ss.station_id;
            """)).mappings().all()  # Converts SQLAlchemy result into dictionaries
        
        return [dict(row) for row in result] if result else []
    
    except SQLAlchemyError as e:
        print(f" Database Error: {e}")
        return []

def get_weather():
    """Fetch the latest weather data from MySQL."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT timestamp, temp, feels_like, temp_min, temp_max, pressure, humidity, wind_speed, wind_gust, 
                       visibility, clouds, sunrise, sunset
                FROM weather
                ORDER BY timestamp DESC
                LIMIT 1;
            """)).mappings().first()  # Get the most recent weather record
        
        return dict(result) if result else {}

    except SQLAlchemyError as e:
        print(f" Database Error: {e}")
        return {}

@app.route('/api/stations', methods=['GET'])
def stations():
    """API endpoint to get station data."""
    return jsonify(get_stations())

@app.route('/api/weather', methods=['GET'])
def weather():
    """API endpoint to get latest weather data."""
    return jsonify(get_weather())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
