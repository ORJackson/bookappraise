import os

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from wtform_fields import *
from models import *

# Configure app
app = Flask(__name__)
app.secret_key = 'CHANGE-LATER'

# Configure database - THIS IS NOT VERY SECURE TO LEAVE DB INFO HERE
app.config['SQLALCHEMY_DATABASE_URI']= 'postgres://xoikhwtplbrmgh:7f40ed19a11bc14c9c1592561e6e220cf3006af8a3202cef51381ee4b49f2462@ec2-54-217-204-34.eu-west-1.compute.amazonaws.com:5432/d2tja8a5tiraod'
db = SQLAlchemy(app)


# Check for environment variable - provided in harvard starter code project 1
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem - provided in harvard starter code project 1
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database - provided in harvard starter code project 1 - CAUSES ERROR, CONFLICTS WITH LINE 16/17 (I think)
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        #check if username already exists
        user_object = User.query.filter_by(username=username).first()
        if user_object:
            return "This username is already taken."

        #but if username is available.... (first value is name of the column, second value is the user input from the form)
        #Add the user to the DB...
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return "Inserted into DB!"
        return "Welcome to the club! Registration successful."
    return render_template("index.html", form=reg_form)

@app.route("/search", methods=['GET', 'POST'])
def search():
    return render_template("search.html")

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    return render_template("logout.html")


# @app.route("/<string:name>")
# def hello(name):
#     name = name.capitalize()
#     return f"Hello, {name}!"

if __name__ == "__main__":
    app.run(debug=True)

