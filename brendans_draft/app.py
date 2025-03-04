from flask import Flask, jsonify, request, render_template
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

### Serve HTML Page (Fix 404 Error) ###
@app.route("/")
def index():
    """Render the main page with Google Maps."""
    return render_template("index.html", google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY"))

###  User Authentication Routes ###
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

            access_token = create_access_token(identity=str(user_id))
            return jsonify({"message": "Login successful!", "token": access_token}), 200

    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error: {e}"}), 500

### Data Retrieval Functions ###
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
            # Fetch latest `current` weather data
            current_result = connection.execute(text("""
                SELECT dt, temp, feels_like, humidity, wind_speed, clouds
                FROM current
                ORDER BY dt DESC
                LIMIT 1;
            """)).mappings().first()

            # Fetch next 5 hours of `hourly` forecast
            hourly_result = connection.execute(text("""
                 SELECT dt, temp, feels_like, humidity, wind_speed, clouds, pop
                 FROM hourly
                 WHERE DATE(dt) = CURDATE()  -- Only today's data
                 ORDER BY dt DESC  -- Get most recent data first
                 LIMIT 5;
            """)).mappings().all()

            # Fetch next 3 days of `daily` forecast
            daily_result = connection.execute(text("""
                SELECT dt, temp_day, temp_min, temp_max, humidity, wind_speed, clouds, pop
                FROM daily
                ORDER BY dt ASC
                LIMIT 3;
            """)).mappings().all()

        return {
            "current": dict(current_result) if current_result else {},
            "hourly": [dict(row) for row in hourly_result] if hourly_result else [],
            "daily": [dict(row) for row in daily_result] if daily_result else []
        }


    except SQLAlchemyError as e:
        print(f"Database Error: {e}")
        return {}

### **4️ Protected API Endpoints ###
@app.route('/api/stations', methods=['GET'])
@jwt_required()
def stations():
    """Protected API endpoint to get station data."""
    return jsonify(get_stations())

@app.route('/api/weather', methods=['GET'])
@jwt_required()
def weather():
    """Protected API endpoint to get latest weather data from `current`, `hourly`, and `daily` tables."""
    return jsonify(get_weather())

### Run Flask App ###
if __name__ == '__main__':
    print("Starting Flask app on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
