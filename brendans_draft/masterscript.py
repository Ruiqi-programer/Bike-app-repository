import time
import logging
from db import create_database, create_tables
from weather import update_weather  # Import weather function
from bike_data import insert_bike_data  # Import bike function

# Configure logging
logging.basicConfig(
    filename="masterscript.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Ensure database & tables exist
create_database()
create_tables()

# Start data collection loop
start_time = time.time()
duration = 12 * 60 * 60  # 12 hours
last_weather_update = 0  # Track last weather update time

logging.info(" Masterscript started. Running for 12 hours...")

while time.time() - start_time < duration:
    try:
        # Update bike data in real time (every 10 seconds)
        logging.info(" Fetching real-time bike station data...")
        insert_bike_data()  # Update bike station data
        logging.info(" Bike data updated successfully.")

        # Update weather data every 1 hour
        current_time = time.time()
        if current_time - last_weather_update >= 3600:  # Ensure hourly weather update
            logging.info(" Fetching weather data...")
            update_weather()  # Update weather data
            last_weather_update = current_time  # Update last weather update timestamp
            logging.info(" Weather data updated successfully.")

    except Exception as e:
        logging.error(f" Error in master script: {e}")

    time.sleep(20)  # Fetch new bike data every 20 seconds (Real-Time Updates)

logging.info(" Finished 12-hour data collection session.")
