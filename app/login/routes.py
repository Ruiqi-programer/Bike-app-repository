from flask import Flask,Blueprint, render_template, request, redirect, url_for, session, flash
import os
import logging
from datetime import datetime
import bcrypt
from functools import wraps
from sqlalchemy import text
from app.models.db import engine

users = Blueprint('users', __name__, template_folder='templates', static_folder='static')

# Configure logging
logging.basicConfig(filename='login_debug.log', 
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('users.login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@users.route('/')
def index():
    return redirect(url_for('users.login'))

@users.route('/login', methods=['GET', 'POST'])
def login():
    error_param = request.args.get('error')
    success_param = request.args.get('success')
    
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        state = request.form.get('state')  
        
        logging.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            return redirect(url_for('users.login', error='Please enter both email and password.'))
        
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT id, fullname, email, password, status FROM users WHERE email = :email"),
                    {"email": email}
                ).fetchone()
                
                if result:
                    user = {
                        'id': result[0],
                        'fullname': result[1],
                        'email': result[2],
                        'password': result[3],
                        'status': result[4]
                    }
                    # Check account status
                    if user['status'] != 'active':
                        return redirect(url_for('users.login', error='This account is not active. Please contact support.', email_prefilled=email))
                    
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
                        conn.execute(
                            text("UPDATE users SET last_login = NOW() WHERE id = :id"),
                            {"id": user['id']}
                        )
                        created_at = conn.execute(
                                text("SELECT created_at FROM users WHERE id = :id"),
                                {"id": user['id']}
                            ).fetchone()[0]
                        session['created_at'] = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                        logging.info(f"Login successful for: {email}")
                        return redirect(url_for('users.dashboard'))
                    else:
                        logging.warning(f"Password verification failed for: {email}")
                        return redirect(url_for('users.login', error='Invalid email or password. Please try again.'))
                else:
                    logging.warning(f"No user found with email: {email}")
                    return redirect(url_for('users.login', error='Invalid email or password. Please try again.'))
                    
        except Exception as e:
            logging.error(f"Login Error: {e}")
            return redirect(url_for('users.login', error='An unexpected error occurred. Please try again later.'))
    
    return render_template('log_in.html', email_prefilled=request.args.get('email_prefilled', ''))

@users.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('users.login', success='You have been successfully logged out.'))

@users.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                          user_fullname=session.get('fullname', ''),
                          user_id=session.get('user_id', ''),
                          fullname=session.get('fullname', ''),
                          email=session.get('email', ''),
                          password=session.get('password', ''),
                          time=session.get('created_at', ''))

@users.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    field = request.form.get('field')
    new_value = request.form.get('new_value')
    user_id = session.get('user_id')
    
    if not field or not new_value or not user_id:
        return redirect(url_for('users.dashboard', error='Invalid update request.'))
    
    try:
        with engine.connect() as conn:
            update_message = ''
            
            if field == 'password':
                # Hash the password for security
                hashed_value = bcrypt.hashpw(new_value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                conn.execute(
                    text("UPDATE users SET password = :hashed_value WHERE id = :id"),
                    {"hashed_value": hashed_value, "id": user_id}
                )
                session['password'] = new_value  # Store plain password in session
            elif field == 'fullname':
                conn.execute(
                    text("UPDATE users SET fullname = :new_value WHERE id = :id"),
                    {"new_value": new_value, "id": user_id}
                )
                session['fullname'] = new_value
            elif field == 'email':
                # Validate email format
                if '@' not in new_value or '.' not in new_value:
                    return redirect(url_for('users.dashboard', error='Invalid email format!'))
                conn.execute(
                    text("UPDATE users SET email = :new_value WHERE id = :id"),
                    {"new_value": new_value, "id": user_id}
                )
                session['email'] = new_value
            
            conn.commit()
            return redirect(url_for('users.dashboard', success=f"{field.capitalize()} updated successfully!"))
            
    except Exception as e:
        logging.error(f"Profile update error: {e}")
        return redirect(url_for('users.dashboard', error=f"Error updating {field}: {e}"))

@users.route('/create_account', methods=['GET', 'POST'])
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
            return redirect(url_for('users.create_account', error=error, fullname=fullname, email=email, terms=terms_accepted))
        
        # Check if email already exists
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT id FROM users WHERE email = :email"),
                    {"email": email}
                ).fetchone()
                
                if result:
                    return redirect(url_for('users.create_account', error="This email is already registered. Please log in or use a different email.", 
                                  fullname=fullname, email=email, terms=terms_accepted))
                
                # Hash password
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Insert user into database
                result = conn.execute(
                    text("INSERT INTO users (fullname, email, password, terms_accepted, created_at) VALUES (:fullname, :email, :password, :terms_accepted, :created_at)"),
                    {
                        "fullname": fullname,
                        "email": email,
                        "password": hashed_password,
                        "terms_accepted": terms_accepted,
                        "created_at": datetime.now()
                    }
                )
                conn.commit()
                
                # Set session for automatic login
                user_id = result.lastrowid
                session['user_id'] = user_id
                session['user_fullname'] = fullname
                session['fullname'] = fullname
                session['email'] = email
                session['password'] = password
                session['logged_in'] = True
                
                return redirect(url_for('users.dashboard'))
                
        except Exception as e:
            logging.error(f"Registration error: {e}")
            return redirect(url_for('users.create_account', error=f"Registration failed: {e}", 
                          fullname=fullname, email=email, terms=terms_accepted))
    
    return render_template('create_account.html', 
                          fullname=request.args.get('fullname', ''),
                          email=request.args.get('email', ''),
                          terms_accepted=request.args.get('terms', ''))

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        state = request.form.get('state') 
        
        if not email or '@' not in email or '.' not in email:
            return redirect(url_for('users.reset_password', error='Invalid email address.'))
        
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT fullname, email FROM users WHERE email = :email"),
                    {"email": email}
                ).fetchone()
                
                if result:
                    return redirect(url_for('users.login', success='Password reset instructions have been sent to your email. Please check your inbox.'))
                else:
                    return redirect(url_for('users.create_account', error='This email is not registered. Please create a new account.'))
                
        except Exception as e:
            logging.error(f"Password reset error: {e}")
            return redirect(url_for('users.reset_password', error='An error occurred during password reset. Please try again later.'))
    
    return render_template('reset_password.html')

