import json
import logging
from sqlalchemy import create_engine, text
from config import DB_CONFIG

# Configure logging
logging.basicConfig(
    filename="db_import.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Connect to MySQL
connection_string = f"mysql+mysqldb://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string, echo=True)

def load_json(filename):
    """Load data from JSON file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f" File {filename} not found.")
        return None

def insert_bike_data():
    """Extract and insert bike data from JSON."""
    data = load_json("bike_data.json")
    if not data:
        return

    with engine.connect() as connection:
        transaction = connection.begin()
        for station in data:
            static_sql = text("""
                INSERT INTO stations (station_id, contract_name, name, address, latitude, longitude, total_bike_stands)
                VALUES (:station_id, :contract_name, :name, :address, :latitude, :longitude, :total_bike_stands)
                ON DUPLICATE KEY UPDATE 
                    name=VALUES(name), 
                    address=VALUES(address), 
                    total_bike_stands=VALUES(total_bike_stands)
            """)
            connection.execute(static_sql, {
                "station_id": station["number"],
                "contract_name": station["contract_name"],
                "name": station["name"],
                "address": station["address"],
                "latitude": station["position"]["lat"],
                "longitude": station["position"]["lng"],
                "total_bike_stands": station["bike_stands"]
            })

            dynamic_sql = text("""
                INSERT INTO station_status (station_id, available_bikes, available_bike_stands, status, last_update)
                VALUES (:station_id, :available_bikes, :available_bike_stands, :status, NOW())
                ON DUPLICATE KEY UPDATE 
                    available_bikes=VALUES(available_bikes), 
                    available_bike_stands=VALUES(available_bike_stands), 
                    status=VALUES(status)
            """)
            connection.execute(dynamic_sql, {
                "station_id": station["number"],
                "available_bikes": station["available_bikes"],
                "available_bike_stands": station["available_bike_stands"],
                "status": station["status"]
            })
        
        transaction.commit()
        logging.info("🚴 Bike data inserted successfully.")

def insert_weather_data():
    """Extract and insert weather data from JSON."""
    data = load_json("weather_data.json")
    if not data:
        return

    weather_sql = text("""
        INSERT INTO weather (timestamp, temp, feels_like, temp_min, temp_max, pressure, humidity, wind_speed, wind_gust, visibility, clouds, sunrise, sunset)
        VALUES (NOW(), :temp, :feels_like, :temp_min, :temp_max, :pressure, :humidity, :wind_speed, :wind_gust, :visibility, :clouds, :sunrise, :sunset)
        ON DUPLICATE KEY UPDATE 
            temp=VALUES(temp), 
            feels_like=VALUES(feels_like), 
            humidity=VALUES(humidity), 
            wind_speed=VALUES(wind_speed)
    """)

    with engine.connect() as connection:
        connection.execute(weather_sql, {
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "temp_min": data["main"]["temp_min"],
            "temp_max": data["main"]["temp_max"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "wind_gust": data["wind"].get("gust"),
            "visibility": data.get("visibility"),
            "clouds": data["clouds"]["all"],
            "sunrise": data["sys"]["sunrise"],
            "sunset": data["sys"]["sunset"]
        })
    logging.info(" Weather data inserted successfully.")

# Insert the extracted data into the database
insert_bike_data()
insert_weather_data()
