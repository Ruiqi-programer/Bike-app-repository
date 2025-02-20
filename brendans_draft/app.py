from flask import Flask, jsonify
from flask_cors import CORS
<<<<<<< HEAD
<<<<<<< HEAD
import pymysql

app = Flask(__name__)
CORS(app)  # Allow frontend access

# Database connection details
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "admin",
    "password": "password",  
    "database": "database-1",
    "port": 3307 
}

def get_stations():
    """Fetch bike station data including availability from MySQL."""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT s.station_id, s.name, s.latitude, s.longitude, s.total_bike_stands,
               ss.available_bikes, ss.available_bike_stands
        FROM stations s
        JOIN station_status ss ON s.station_id = ss.station_id;
    """
    
    cursor.execute(query)
    stations = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return stations
=======
=======
>>>>>>> 0f2c544 (Updated bike app in brendans_draft)
from sqlalchemy import create_engine, text
from config import DB_CONFIG

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Database connection using SQLAlchemy
connection_string = f"mysql+mysqldb://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string, echo=True)

def get_stations():
    """Fetch bike station data including availability from MySQL."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT s.station_id, s.name, s.latitude, s.longitude, s.total_bike_stands,
                   ss.available_bikes, ss.available_bike_stands
            FROM stations s
            JOIN station_status ss ON s.station_id = ss.station_id;
        """)).mappings().all()  # Converts SQLAlchemy result into dictionaries

    return [dict(row) for row in result]  # Ensures JSON compatibility

def get_weather():
    """Fetch the latest weather data from MySQL."""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT timestamp, temp, feels_like, temp_min, temp_max, pressure, humidity, wind_speed, wind_gust, 
                   visibility, clouds, sunrise, sunset
            FROM weather
            ORDER BY timestamp DESC
            LIMIT 1;
        """)).mappings().first()  # Get the most recent weather record

    return dict(result) if result else {}  # Return empty if no data available
<<<<<<< HEAD
>>>>>>> c120b37 (logging + added weather stats to basic html)
=======
=======
import pymysql

app = Flask(__name__)
CORS(app)  # Allow frontend access

# Database connection details
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "admin",
    "password": "password",  
    "database": "database-1",
    "port": 3307 
}

def get_stations():
    """Fetch bike station data including availability from MySQL."""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT s.station_id, s.name, s.latitude, s.longitude, s.total_bike_stands,
               ss.available_bikes, ss.available_bike_stands
        FROM stations s
        JOIN station_status ss ON s.station_id = ss.station_id;
    """
    
    cursor.execute(query)
    stations = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return stations
>>>>>>> origin/main
>>>>>>> 0f2c544 (Updated bike app in brendans_draft)

@app.route('/api/stations', methods=['GET'])
def stations():
    """API endpoint to get station data."""
    return jsonify(get_stations())

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> 0f2c544 (Updated bike app in brendans_draft)
@app.route('/api/weather', methods=['GET'])
def weather():
    """API endpoint to get latest weather data."""
    return jsonify(get_weather())

<<<<<<< HEAD
>>>>>>> c120b37 (logging + added weather stats to basic html)
=======
=======
>>>>>>> origin/main
>>>>>>> 0f2c544 (Updated bike app in brendans_draft)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
