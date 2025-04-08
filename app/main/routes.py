from flask import Blueprint, render_template,abort,jsonify, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import text
from app.models.db import engine

# 创建主页蓝图
main = Blueprint('main', __name__, template_folder='templates', static_folder='static')

# 主页路由
@main.route('/')
def index():
    reviews = [
        {"name": "Tom Leakar", "location": "London, UK", "image": "images/clients/c1.png", "comment": "Great service! Highly recommend."},
        {"name": "Monirul Islam", "location": "London, UK", "image": "images/clients/c2.png", "comment": "Excellent customer support!"},
        {"name": "Shohrab Hossain", "location": "London, UK", "image": "images/clients/c3.png", "comment": "Fast and reliable, would use again!"},
        {"name": "Jane Doe", "location": "New York, USA", "image": "images/clients/c4.png", "comment": "Outstanding experience!"}
    ]
    return render_template('index.html',reviews=reviews)


@main.route('/faqs')
def faq():
    return render_template("faq.html")

# business page
@main.route('/subscription/<ticket_type>')
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
            "price": "100",
            "ticket_type":"annual"
        },
        {
            "title": "PROMOTION",
            "description": "student discount",
            "price": "10% Discount",
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
    review=StringField("review",validators=[DataRequired()],widget=TextArea())
    submit=SubmitField("Submit")

#create contact and review page
@main.route('/contact',methods=['GET','POST'])
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