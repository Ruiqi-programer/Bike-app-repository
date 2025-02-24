from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from config import DB_CONFIG  

# Create base engine without specifying a database
base_connection_string = f"mysql+mysqldb://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
base_engine = create_engine(base_connection_string, echo=True)

def create_database():
    """Ensure the database exists before proceeding."""
    db_name = DB_CONFIG['database']
    
    try:
        with base_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name};"))
            print(f" Database '{db_name}' is ready.")
    except OperationalError as e:
        print(f" Error connecting to MySQL: {e}")
        exit(1)

# Create the database if it doesn't exist
create_database()

# Connect to the actual database
connection_string = f"{base_connection_string}/{DB_CONFIG['database']}"
engine = create_engine(connection_string, echo=True)

def create_tables():
    """Create required database tables for bikes and weather."""
    with engine.connect() as connection:
        connection.execute(text(""" 
            CREATE TABLE IF NOT EXISTS stations (
                station_id INT PRIMARY KEY,
                contract_name VARCHAR(50),
                name VARCHAR(255),
                address VARCHAR(255),
                latitude DOUBLE,
                longitude DOUBLE,
                total_bike_stands INT
            )
        """))

        connection.execute(text(""" 
            CREATE TABLE IF NOT EXISTS station_status (
                station_id INT,
                available_bikes INT,
                available_bike_stands INT,
                status VARCHAR(20),
                last_update DATETIME,
                PRIMARY KEY (station_id, last_update),
                FOREIGN KEY (station_id) REFERENCES stations(station_id) ON DELETE CASCADE
            )
        """))

        connection.execute(text(""" 
            CREATE TABLE IF NOT EXISTS weather (
                timestamp DATETIME PRIMARY KEY DEFAULT CURRENT_TIMESTAMP,
                temp FLOAT,
                feels_like FLOAT,
                temp_min FLOAT,
                temp_max FLOAT,
                pressure INT,
                humidity INT,
                wind_speed FLOAT,
                wind_gust FLOAT NULL,
                visibility INT NULL,
                clouds INT NULL,
                sunrise INT,  -- Store Unix timestamp
                sunset INT    -- Store Unix timestamp
            )
        """))

    print(" Database tables checked/created successfully!")

# Ensure tables are created
create_tables()
