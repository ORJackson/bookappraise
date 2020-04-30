import os

from flask import Flask, session, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from wtform_fields import *

app = Flask(__name__)
app.secret_key = 'CHANGE-LATER'

# Check for environment variable - harvard starter project 1
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem - harvard starter project 1
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database - harvard starter project 1
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
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

