from flask import Flask, jsonify
from flask_cors import CORS
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

@app.route('/api/stations', methods=['GET'])
def stations():
    """API endpoint to get station data."""
    return jsonify(get_stations())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
