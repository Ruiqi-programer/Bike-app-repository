from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime
import bcrypt
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

# Configure logging
logging.basicConfig(filename='login_debug.log', 
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'grq990823',
    'database': 'dublinbikesystem',
    'port': 3306
}

# Helper function to get database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        logging.error(f"Database connection error: {e}")
        return None

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_param = request.args.get('error')
    success_param = request.args.get('success')
    
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        state = request.form.get('state')  
        
        logging.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            return redirect(url_for('login', error='Please enter both email and password.'))
        
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('login', error='Database connection error. Please try again later.'))
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, fullname, email, password, status FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                # Check account status
                if user['status'] != 'active':
                    return redirect(url_for('login', error='This account is not active. Please contact support.', email_prefilled=email))
                
                # Verify password
                stored_password = user['password'].encode('utf-8') if isinstance(user['password'], str) else user['password']
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    # Password is correct - Set session variables
                    session['user_id'] = user['id']
                    session['fullname'] = user['fullname']
                    session['email'] = user['email']
                    session['password'] = password  # Store plain password (consider security implications)
                    session['logged_in'] = True
                    
                    # Update last login timestamp
                    cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
                    conn.commit()
                    
                    logging.info(f"Login successful for: {email}")
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('login', error='Invalid email or password. Please try again.'))
                    logging.warning(f"Password verification failed for: {email}")
            else:
                return redirect(url_for('login', error='Invalid email or password. Please try again.'))
                logging.warning(f"No user found with email: {email}")
                
        except Error as e:
            logging.error(f"Login Error: {e}")
            return redirect(url_for('login', error='An unexpected error occurred. Please try again later.'))
        finally:
            cursor.close()
            conn.close()
    
    return render_template('log_in.html', email_prefilled=request.args.get('email_prefilled', ''))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login', success='You have been successfully logged out.'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                          user_fullname=session.get('fullname', ''),
                          user_id=session.get('user_id', ''),
                          fullname=session.get('fullname', ''),
                          email=session.get('email', ''),
                          password=session.get('password', ''),
                          time=session.get('created_at', ''))

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    field = request.form.get('field')
    new_value = request.form.get('new_value')
    user_id = session.get('user_id')
    
    if not field or not new_value or not user_id:
        return redirect(url_for('dashboard', error='Invalid update request.'))
    
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('dashboard', error='Database connection error. Please try again later.'))
    
    try:
        cursor = conn.cursor()
        update_message = ''
        
        if field == 'password':
            # Hash the password for security
            hashed_value = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_value, user_id))
            session['password'] = new_value  # Store plain password in session
        elif field == 'fullname':
            cursor.execute("UPDATE users SET fullname = %s WHERE id = %s", (new_value, user_id))
            session['fullname'] = new_value
        elif field == 'email':
            # Validate email format
            if '@' not in new_value or '.' not in new_value:
                return redirect(url_for('dashboard', error='Invalid email format!'))
            cursor.execute("UPDATE users SET email = %s WHERE id = %s", (new_value, user_id))
            session['email'] = new_value
        
        conn.commit()
        return redirect(url_for('dashboard', success=f"{field.capitalize()} updated successfully!"))
        
    except Error as e:
        conn.rollback()
        logging.error(f"Profile update error: {e}")
        return redirect(url_for('dashboard', error=f"Error updating {field}: {e}"))
    finally:
        cursor.close()
        conn.close()

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm-password', '')
        terms_accepted = 1 if request.form.get('terms') else 0
        
        # Validation
        error = None
        if not fullname or not email or not password:
            error = "All fields are required."
        elif '@' not in email or '.' not in email:
            error = "Invalid email format."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif len(password) < 8 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
            error = "Password must be at least 8 characters long and include uppercase letters, lowercase letters, and numbers."
        elif not terms_accepted:
            error = "You must accept the terms and conditions."
        
        if error:
            return redirect(url_for('create_account', error=error, fullname=fullname, email=email, terms=terms_accepted))
        
        # Check if email already exists
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('create_account', error='Database connection error. Please try again later.', 
                          fullname=fullname, email=email, terms=terms_accepted))
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return redirect(url_for('create_account', error="This email is already registered. Please log in or use a different email.", 
                              fullname=fullname, email=email, terms=terms_accepted))
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert user into database
            cursor.execute(
                "INSERT INTO users (fullname, email, password, terms_accepted, created_at) VALUES (%s, %s, %s, %s, %s)",
                (fullname, email, hashed_password, terms_accepted, datetime.now())
            )
            conn.commit()
            
            # Set session for automatic login
            session['user_id'] = cursor.lastrowid
            session['user_fullname'] = fullname
            session['fullname'] = fullname
            session['email'] = email
            session['password'] = password
            session['logged_in'] = True
            
            return redirect(url_for('dashboard'))
            
        except Error as e:
            logging.error(f"Registration error: {e}")
            return redirect(url_for('create_account', error=f"Registration failed: {e}", 
                          fullname=fullname, email=email, terms=terms_accepted))
        finally:
            cursor.close()
            conn.close()
    
    return render_template('create_account.html', 
                          fullname=request.args.get('fullname', ''),
                          email=request.args.get('email', ''),
                          terms_accepted=request.args.get('terms', ''))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        state = request.form.get('state') 
        
        if not email or '@' not in email or '.' not in email:
            return redirect(url_for('reset_password', error='Invalid email address.'))
        
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('reset_password', error='Database connection error. Please try again later.'))
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT fullname, email FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                return redirect(url_for('login', success='Password reset instructions have been sent to your email. Please check your inbox.'))
            else:
                return redirect(url_for('create_account', error='This email is not registered. Please create a new account.'))
            
        except Error as e:
            logging.error(f"Password reset error: {e}")
            return redirect(url_for('reset_password', error='An error occurred during password reset. Please try again later.'))
        finally:
            cursor.close()
            conn.close()
    
    return render_template('reset_password.html')

@app.route('/initialize_db')
def initialize_db():
    conn = None
    try:
        # Connect to MySQL server (without specifying a database)
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create users table
        cursor.execute("""
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
        """)
        
        conn.commit()
        return "Database initialized successfully!"
    
    except Error as e:
        return f"Database initialization error: {e}"
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)