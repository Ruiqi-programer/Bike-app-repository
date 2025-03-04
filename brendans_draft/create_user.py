from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DB_CONFIG

# Set up database connection
connection_string = f"mysql+mysqldb://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(connection_string, echo=True)

# User details (CHANGE THESE)
username = "brendan"  
email = "brendan1@example.com"  
password = "bike123"  

# Hash the password
hashed_password = generate_password_hash(password)

# Insert user into database
try:
    with engine.connect() as connection:
        transaction = connection.begin()  
        connection.execute(
            text("INSERT INTO users (username, email, password_hash) VALUES (:username, :email, :password)"),
            {"username": username, "email": email, "password": hashed_password}
        )
        transaction.commit()  # 🔹 Explicitly commit
        print(" User created successfully!")
except SQLAlchemyError as e:
    print(f" Error creating user: {e}")
