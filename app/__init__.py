from flask import Flask, render_template,jsonify, request,abort,flash, redirect, url_for,session
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from sqlalchemy import text
from datetime import datetime
import bcrypt
from functools import wraps
import logging
import os
import pandas as pd
from app.machine_learning.model_utils import predict
from app.models.db import engine, create_database, create_tables
from app.models.db import engine
from config import Config



def create_app():
    app = Flask(__name__)

    # Session configuration
    app.secret_key = os.urandom(24)  # For session management
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes

    # Initialize CSRF protection
    CSRFProtect(app)

    #create custom error pages
    #invalid URL 
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"),404
    #Internal Server Error
    @app.errorhandler(500)
    def page_not_found(e):
        return render_template("500.html"),500
    
    @app.route('/to_be_continued')
    def tobecontinue():
        return render_template("tobecontinue.html")

    #first page
    @app.route('/')
    def index():
        reviews = [
            {"name": "Shuangning Wei", "location": "Ralto, Dublin", "image": "images/clients/c2.png", "comment": "Quick, reliable, and cheaper than any other way to get around the city."},
            {"name": "Ruiqi Guo", "location": "Dandrum,Dublin", "image": "images/clients/c4.png", "comment": "Perfect for getting to class on time without the stress of buses!"},
            {"name": "Shohrab Hossain", "location": "3Arena, Dublin", "image": "images/clients/c3.png", "comment": "I ride daily knowing I’m reducing my carbon footprint with every trip"},
            {"name": "Tom Leakar", "location": "Abbey Street, Dublin", "image": "images/clients/c1.png", "comment": "Loved exploring Dublin on two wheels—easy to use and so much fun!"},
            {"name": "Lily Bond", "location": "Fourcourts, Dublin", "image": "images/clients/c5.png", "comment": "A great weekend option for riding with the kids—safe and simple."}
        ]
        return render_template('index.html',reviews=reviews)

    @app.route("/map")
    def map():
        return render_template("stations.html",google_maps_api_key=Config.GOOGLE_MAPS_API_KEY)

    @app.route("/api/weather", methods=["GET"])
    def weather():
        try:
            with engine.connect() as connection:
                # Current weather
                current_result = connection.execute(text("""
                    SELECT dt, temp, feels_like, humidity, wind_speed, clouds
                    FROM current
                    ORDER BY dt DESC
                    LIMIT 1;
                """)).mappings().first()

                # Next 12 hours
                hourly_result = connection.execute(text("""
                    SELECT dt, temp, feels_like, humidity, wind_speed, clouds, pop
                    FROM hourly
                    WHERE dt >= NOW()
                    ORDER BY dt ASC
                    LIMIT 12;
                """)).mappings().all()

                # Next 8 days
                daily_result = connection.execute(text("""
                    SELECT dt, temp_day, temp_min, temp_max, humidity, wind_speed, clouds, pop, weather_desc, weather_icon
                    FROM daily
                    ORDER BY dt ASC
                    LIMIT 8;
                """)).mappings().all()

            return jsonify({
                "current": dict(current_result) if current_result else {},
                "hourly": [dict(row) for row in hourly_result],
                "daily": [dict(row) for row in daily_result]
            })

        except Exception as e:
            print("❌ Weather DB error:", e)
            return jsonify({"error": "Could not fetch weather"}), 500

    @app.route("/api/stations", methods=["GET"])
    def api_stations():
        try:
            with engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT s.station_id, s.name, s.latitude, s.longitude, s.total_bike_stands,
                        ss.available_bikes, ss.available_bike_stands
                    FROM stations s
                    JOIN (
                        SELECT station_id, available_bikes, available_bike_stands
                        FROM station_status
                        WHERE (station_id, last_update) IN (
                            SELECT station_id, MAX(last_update)
                            FROM station_status
                            GROUP BY station_id
                        )
                    ) ss ON s.station_id = ss.station_id;
                """)).mappings().all()

            return jsonify([dict(row) for row in result])

        except Exception as e:
            print("❌ Station DB error:", e)
            return jsonify({"error": "Could not fetch stations"}), 500
        

    @app.route("/predict", methods=["GET"])
    def predict_route():
        try:
            date = request.args.get("date")
            time = request.args.get("time")
            station_id = request.args.get("station_id")

            if not all([date, time, station_id]):
                return jsonify({"error": "Missing date, time, or station_id"}), 400

            result = predict(station_id, date, time)
            if isinstance(result, dict) and "error" in result:
                return jsonify(result), 500
            return jsonify({"predicted_available_bikes": result})

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route("/predict_range", methods=["GET"])
    def predict_range():
        try:
            date = request.args.get("date")
            time = request.args.get("time")
            station_id = request.args.get("station_id")

            if not all([date, time, station_id]):
                return jsonify({"error": "Missing date, time, or station_id"}), 400
   
            result = predict(station_id, date, time)

            if isinstance(result, dict) and "error" in result:
                return jsonify(result), 500
            return jsonify({"predicted_available_bikes": result})

        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/faqs')
    def faq():
        return render_template("faq.html")

    # business page
    @app.route('/subscription/<ticket_type>')
    def business(ticket_type):
        subscription_options = [
            {
                "title": "1 DAY TICKET",
                "description": """For short term hire, a 1 Day Ticket will give you access to all
                the benefits of the dublinbikes service. Ideal for day-trippers,
                tourists and visitors as a way of getting around and exploring the
                city. The first 30 minutes of each journey is free. After this
                rental charges are applied Available from 5am to 12.30am daily
                Bikes can be returned 24/7""",
                "price": "3",
                "ticket_type":"oneday"
                
            },
            {
                "title": "3 DAY TICKET",
                "description": """For short term hire, a 3 Day Ticket will give you access to all
                the benefits of the dublinbikes service. Ideal for tourists and
                visitors as a way of getting around and exploring the city. The
                first 30 minutes of each journey is free. After this rental
                charges are applied. """,
                "price": "5",
                "ticket_type":"threedays"
                
            },
            {
                "title": "ANNUAL SUBSCRIPTION",
                "description": """With an Annual Subscription you can rent a bike 365 days a year
                for an annual fee of €35. The first 30 minutes of each journey is
                free, after this rental charges apply. """,
                "price": "35",
                "ticket_type":"annual"
            },
            {
                "title": "PROMOTION",
                "description": """Exclusive offer for students - enjoy the same benefits of an annual subscription at
                a discounted rate! Valid student ID required at registration.""",
                "price": "31.50",
                "ticket_type":"discount"
            }
        ]
            # 根据 ticket_type 找到对应订阅信息
        selected = next((opt for opt in subscription_options if opt["ticket_type"] == ticket_type), None)

        if selected:
            return render_template('business.html', subscription_options=subscription_options, selected=selected)
        else:
            abort(404)


    # create a Form class
    class ReviewForm(FlaskForm):
        name=StringField("Name",validators=[DataRequired()])
        email=StringField("Email",validators=[DataRequired()])
        phone=StringField("Telephone",validators=[DataRequired()])
        review=StringField("Review",validators=[DataRequired()],widget=TextArea())
        submit=SubmitField("Submit")

    #create contact and review page
    @app.route('/contact',methods=['GET','POST'])
    def contact():
        name = None
        form = ReviewForm()
        if form.validate_on_submit():
            try:
                with engine.connect() as conn:
                    with conn.begin():
                        # Check if email or phone already exists
                        existing_user = conn.execute(
                            text("SELECT id FROM contact_reviews WHERE email = :email OR phone = :phone"),
                            {"email": form.email.data, "phone": form.phone.data}
                        ).fetchone()
                        
                        if existing_user:
                            flash("A submission with this email or phone number already exists.", "error")
                        else:
                            # Insert new contact review
                            conn.execute(
                                text("""
                                    INSERT INTO contact_reviews (name, email, phone, review, date_added)
                                    VALUES (:name, :email, :phone, :review, :date_added)
                                """),
                                {
                                    "name": form.name.data,
                                    "email": form.email.data,
                                    "phone": form.phone.data,
                                    "review": form.review.data,
                                    "date_added": datetime.utcnow()
                                }
                            )
                            name = form.name.data
                            # Clear the form
                            form.name.data = ''
                            form.email.data = ''
                            form.phone.data = ''
                            form.review.data = ''
                            flash("We've received your message successfully!", "success")
            except Exception as e:
                flash(f"Error submitting your message: {e}", "error")
        
        # Fetch all reviews (optional, if you want to display them)
        with engine.connect() as conn:
            our_users = conn.execute(
                text("SELECT * FROM contact_reviews ORDER BY date_added DESC")
            ).fetchall()
        
        return render_template("contact.html", form=form, name=name, our_users=our_users)


    # Login required decorator
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function


    # Configure logging
    logging.basicConfig(filename='login_debug.log', 
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    # Routes
    # @app.route('/')
    # def index():
    #     return redirect(url_for('login'))

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
                            return redirect(url_for('index'))
                        else:
                            logging.warning(f"Password verification failed for: {email}")
                            return redirect(url_for('login', error='Invalid email or password. Please try again.'))
                    else:
                        logging.warning(f"No user found with email: {email}")
                        return redirect(url_for('login', error='Invalid email or password. Please try again.'))
                        
            except Exception as e:
                logging.error(f"Login Error: {e}")
                return redirect(url_for('login', error='An unexpected error occurred. Please try again later.'))
        
        return render_template('log_in.html', email_prefilled=request.args.get('email_prefilled', ''))

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index', success='You have been successfully logged out.'))

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
            return redirect(url_for('dashboard', error=f"Error updating {field}: {e}"))

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
            try:
                with engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT id FROM users WHERE email = :email"),
                        {"email": email}
                    ).fetchone()
                    
                    if result:
                        return redirect(url_for('create_account', error="This email is already registered. Please log in or use a different email.", 
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
                    
                    return redirect(url_for('dashboard'))
                    
            except Exception as e:
                logging.error(f"Registration error: {e}")
                return redirect(url_for('create_account', error=f"Registration failed: {e}", 
                            fullname=fullname, email=email, terms=terms_accepted))
        
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
            
            try:
                with engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT fullname, email FROM users WHERE email = :email"),
                        {"email": email}
                    ).fetchone()
                    
                    if result:
                        return redirect(url_for('login', success='Password reset instructions have been sent to your email. Please check your inbox.'))
                    else:
                        return redirect(url_for('create_account', error='This email is not registered. Please create a new account.'))
                    
            except Exception as e:
                logging.error(f"Password reset error: {e}")
                return redirect(url_for('reset_password', error='An error occurred during password reset. Please try again later.'))
        
        return render_template('reset_password.html')

    # 加载配置
    app.config.from_object('config.Config')
    
    # 初始化 CORS
    CORS(app)
    
    # 初始化数据库
    create_database()
    create_tables()

    return app