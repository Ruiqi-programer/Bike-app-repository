# db.py

from sqlalchemy import create_engine, text
from config import DB_CONFIG

# Create SQLAlchemy engine
connection_string = f"mysql+mysqldb://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
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
                station_id INT PRIMARY KEY,
                available_bikes INT,
                available_bike_stands INT,
                status VARCHAR(20),
                last_update DATETIME,
                FOREIGN KEY (station_id) REFERENCES stations(station_id) ON DELETE CASCADE
            )
        """))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS weather (
                timestamp DATETIME PRIMARY KEY,
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
                sunrise DATETIME,
                sunset DATETIME
            )
        """))

    print(" Database tables checked/created successfully!")

# Ensure tables are created when db.py is imported
create_tables()
