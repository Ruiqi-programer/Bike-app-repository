from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DB_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Set JWT Secret Key
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback_key_if_not_set")
jwt = JWTManager(app)

# Database connection
connection_string = f"mysql+mysqldb://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string, echo=True)

### USER AUTHENTICATION ###
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    hashed_password = generate_password_hash(password)

    try:
        with engine.connect() as connection:
            existing_user = connection.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            ).fetchone()

            if existing_user:
                return jsonify({"error": "Email already registered"}), 409

            connection.execute(
                text("INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password)"),
                {"username": username, "email": email, "password": hashed_password}
            )

        return jsonify({"message": "User registered successfully!"}), 201

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return jsonify({"error": f"Database error: {e}"}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token."""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Both email and password are required"}), 400

    try:
        with engine.connect() as connection:
            user = connection.execute(
                text("SELECT id, password_hash FROM users WHERE email = :email"),
                {"email": email}
            ).fetchone()

            if not user:
                return jsonify({"error": "Invalid credentials"}), 401

            user_id, stored_hash = user

            if not check_password_hash(stored_hash, password):
                return jsonify({"error": "Invalid credentials"}), 401

            #  Convert user_id to string
            access_token = create_access_token(identity=str(user_id))  
            return jsonify({"message": "Login successful!", "token": access_token}), 200

    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error: {e}"}), 500


### DATA RETRIEVAL FUNCTIONS ###
def get_stations():
    """Fetch bike station data including availability from MySQL."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT s.station_id, s.name, s.latitude, s.longitude, s.total_bike_stands,
                       ss.available_bikes, ss.available_bike_stands
                FROM stations s
                JOIN station_status ss ON s.station_id = ss.station_id;
            """)).mappings().all()

        return [dict(row) for row in result] if result else []
    
    except SQLAlchemyError as e:
        print(f"Database Error: {e}")
        return []


def get_weather():
    """Fetch latest weather data from MySQL."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT timestamp, temp, feels_like, humidity, wind_speed, clouds
                FROM weather
                ORDER BY timestamp DESC
                LIMIT 1;
            """)).mappings().first()

        return dict(result) if result else {}

    except SQLAlchemyError as e:
        print(f"Database Error: {e}")
        return {}


### PROTECTED API ENDPOINTS ###
@app.route('/api/stations', methods=['GET'])
@jwt_required()
def stations():
    """Protected API endpoint to get station data."""
    user_id = get_jwt_identity()
    print(f"🛑 DEBUG: User ID from JWT: {user_id} (Type: {type(user_id)})")

    if not isinstance(user_id, str):  # Ensure it’s a string
        return jsonify({"error": "Invalid JWT identity format"}), 400

    return jsonify(get_stations())


@app.route('/api/weather', methods=['GET'])
@jwt_required()
def weather():
    """Protected API endpoint to get latest weather data."""
    user_id = get_jwt_identity()
    print(f"User {user_id} accessed weather data")

    weather_data = get_weather()
    return jsonify(weather_data)


### RUN FLASK APP ###
if __name__ == '__main__':
    print("Starting Flask app on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
