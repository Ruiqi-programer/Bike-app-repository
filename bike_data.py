import requests
import logging
from sqlalchemy import create_engine, text
from db import engine  # Import database engine
from config import BIKE_API_URL  # Import API URL

# Configure logging
logging.basicConfig(
    filename="db_import.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def fetch_bike_data():
    """Fetch real-time bike station data from JCDecaux API."""
    try:
        response = requests.get(BIKE_API_URL, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP errors (4xx, 5xx)
        return response.json()  # Return JSON data
    except requests.exceptions.RequestException as e:
        logging.error(f" JCDecaux API Request Error: {e}")
        return None

def insert_bike_data():
    """Fetch live data from API and insert bike station data into MySQL."""
    data = fetch_bike_data()

    if not data:
        print(" No bike data fetched from API.")
        return

    with engine.connect() as connection:
        transaction = connection.begin()
        for station in data:
            # Insert static bike station details
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

            # Insert dynamic station status (availability)
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
        logging.info(" Live bike data inserted successfully.")
        print(" Live bike station data updated successfully!")

# Run function directly if this script is executed
if __name__ == "__main__":
    insert_bike_data()
