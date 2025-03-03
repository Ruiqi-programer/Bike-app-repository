from flask import Flask,render_template,request,flash
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
from dotenv import load_dotenv
import os

load_dotenv()
#flask instance
app = Flask(__name__,static_folder="static")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret')

#create a form class
class NamerForm(FlaskForm):
    name=StringField("What's your name",validators=[DataRequired()])
    submit=SubmitField("Submit")



@app.route('/')
def index():
    reviews = [
        {"name": "Tom Leakar", "location": "London, UK", "image": "images/clients/c1.png", "comment": "Great service! Highly recommend."},
        {"name": "Monirul Islam", "location": "London, UK", "image": "images/clients/c2.png", "comment": "Excellent customer support!"},
        {"name": "Shohrab Hossain", "location": "London, UK", "image": "images/clients/c3.png", "comment": "Fast and reliable, would use again!"},
        {"name": "Jane Doe", "location": "New York, USA", "image": "images/clients/c4.png", "comment": "Outstanding experience!"}
    ]
    return render_template('index.html', reviews=reviews)


@app.route("/user/<name>")
def user(name):
    return render_template("user.html",name=name)

@app.route("/greet")
def greet():
    name=request.args.get('name','Guest')
    return f"hello,{name}"



#Create name page
@app.route('/name',methods=['GET','POST'])
def name():
    name=None
    form=NamerForm()
    #validate form
    if form.validate_on_submit():
        name=form.name.data
        form.name.data=''
        flash("Form submitted successfully")

    return render_template("name.html",name=name,form=form)


@app.route('/company')
def company():
    return render_template("company.html")

@app.route('/faqs')
def faq():
    return render_template("faq.html")

#create custom error pages
#invalid URL 
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404
#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"),500

if __name__ == "__main__":
    app.run(debug=True)