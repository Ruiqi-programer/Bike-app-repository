from sqlalchemy import create_engine, text
from config import Config
from sqlalchemy.exc import OperationalError

# Create engine without specifying the database
base_connection_string = f"mysql+pymysql://{Config.DB_CONFIG['user']}:{Config.DB_CONFIG['password']}@{Config.DB_CONFIG['host']}:{Config.DB_CONFIG['port']}"

base_engine = create_engine(base_connection_string, echo=True)

# Create database if it doesn't exist
def create_database():
    """Check if the database exists and create it if necessary."""
    db_name = Config.DB_CONFIG['database']

    try:
        with base_engine.connect() as connection:
            result = connection.execute(text(f"SHOW DATABASES LIKE '{db_name}';")).fetchone()
            if not result:
                print(f" Database '{db_name}' does not exist. Creating...")
                connection.execute(text(f"CREATE DATABASE {db_name};"))
                print(f" Database '{db_name}' created successfully.")
    except OperationalError as e:
        print(f" Error connecting to MySQL: {e}")
        exit(1)





# Connect using the actual database
connection_string = f"{base_connection_string}/{Config.DB_CONFIG['database']}"
engine = create_engine(connection_string, echo=True)

# create tables
def create_tables():
    """Create required database tables for bikes and weather."""
    with engine.connect() as connection:
        # Create bike station tables
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

        # Create `current` weather table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS current (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lat FLOAT NOT NULL,
                lon FLOAT NOT NULL,
                timezone VARCHAR(50),
                timezone_offset INT,
                dt DATETIME NOT NULL,
                sunrise DATETIME NOT NULL,
                sunset DATETIME NOT NULL,
                temp FLOAT NOT NULL,
                feels_like FLOAT NOT NULL,
                pressure INT NOT NULL,
                humidity INT NOT NULL,
                dew_point FLOAT NOT NULL,
                uvi FLOAT DEFAULT 0.0,
                clouds INT NOT NULL,
                visibility INT DEFAULT 10000,
                wind_speed FLOAT NOT NULL,
                wind_deg INT NOT NULL,
                wind_gust FLOAT DEFAULT NULL,
                weather_id INT NOT NULL,
                weather_main VARCHAR(50),
                weather_desc VARCHAR(100),
                weather_icon VARCHAR(10)
            )
        """))

        # Create `hourly` weather table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS hourly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lat FLOAT NOT NULL,
                lon FLOAT NOT NULL,
                timezone VARCHAR(50),
                timezone_offset INT,
                dt DATETIME NOT NULL,
                temp FLOAT NOT NULL,
                feels_like FLOAT NOT NULL,
                pressure INT NOT NULL,
                humidity INT NOT NULL,
                dew_point FLOAT NOT NULL,
                uvi FLOAT DEFAULT 0.0,
                clouds INT NOT NULL,
                visibility INT DEFAULT 10000,
                wind_speed FLOAT NOT NULL,
                wind_deg INT NOT NULL,
                wind_gust FLOAT DEFAULT NULL,
                weather_id INT NOT NULL,
                weather_main VARCHAR(50),
                weather_desc VARCHAR(100),
                weather_icon VARCHAR(10),
                pop FLOAT NOT NULL
            )
        """))

        # Create `daily` weather table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS daily (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lat FLOAT NOT NULL,
                lon FLOAT NOT NULL,
                timezone VARCHAR(50),
                timezone_offset INT,
                dt DATETIME NOT NULL,
                sunrise DATETIME NOT NULL,
                sunset DATETIME NOT NULL,
                moonrise DATETIME NOT NULL,
                moonset DATETIME NOT NULL,
                moon_phase FLOAT NOT NULL,
                summary TEXT,
                temp_day FLOAT NOT NULL,
                temp_min FLOAT NOT NULL,
                temp_max FLOAT NOT NULL,
                temp_night FLOAT NOT NULL,
                temp_eve FLOAT NOT NULL,
                temp_morn FLOAT NOT NULL,
                feels_like_day FLOAT NOT NULL,
                feels_like_night FLOAT NOT NULL,
                feels_like_eve FLOAT NOT NULL,
                feels_like_morn FLOAT NOT NULL,
                pressure INT NOT NULL,
                humidity INT NOT NULL,
                dew_point FLOAT NOT NULL,
                wind_speed FLOAT NOT NULL,
                wind_deg INT NOT NULL,
                wind_gust FLOAT DEFAULT NULL,
                clouds INT NOT NULL,
                uvi FLOAT DEFAULT 0.0,
                pop FLOAT NOT NULL,
                rain FLOAT DEFAULT 0.0,
                weather_id INT NOT NULL,
                weather_main VARCHAR(50),
                weather_desc VARCHAR(100),
                weather_icon VARCHAR(10)
            )
        """))

 # Create `users` table 
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                terms_accepted TINYINT(1) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL,
                last_login DATETIME,
                status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
                verification_token VARCHAR(255),
                is_verified TINYINT(1) DEFAULT 0,
                reset_token VARCHAR(255),
                reset_token_expiry DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))

     # Create `contact_reviews` table for storing contact form submissions
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS contact_reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                email VARCHAR(120) NOT NULL,
                phone VARCHAR(120) NOT NULL,
                review TEXT,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (email),
                UNIQUE (phone)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """))


    print(" Database tables checked/created successfully!")

