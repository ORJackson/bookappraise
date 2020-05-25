import os

from flask import Flask, session, render_template, redirect, url_for, request, flash
from flask_session import Session
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import LoginManager, login_user, current_user, logout_user

from flask_sqlalchemy import SQLAlchemy 

from wtform_fields import *
from models import *
from tables import Results

import string
import requests

# secret_key and database info stored in .env
# Configure app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', None)

# Configure database - using Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI']= os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

#My config using SQLAlchemy:

# engine = create_engine(os.getenv("DATABASE_URL"))
# db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Set up database - provided in harvard starter code project 1 - CAUSES ERROR
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))

# Check for environment variable - provided in harvard starter code project 1
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem - provided in harvard starter code project 1
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure flask login
login = LoginManager(app)
login.init_app(app)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form = RegistrationForm()

    #if the validation is successful updates the database
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        #Hash password
        hashed_password = pbkdf2_sha256.hash(password)
        
        #Add the user to the DB... (first value is name of the column, second value is the user input from the form)
        # user = User(username=username, password=hashed_password)
        # db.session.add(user)
        # db.session.commit()

        db.session.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password" : hashed_password})
        db.session.commit()

        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)


@app.route("/login", methods=['GET', 'POST'])
def login():

    login_form = LoginForm()

    # Allow login if validation is successful
    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        return redirect(url_for('search'))

    #Allow login if validation is successful - ERROR
    # username = login_form.username.data
       
    # if login_form.validate_on_submit():
    #     user_object = db.session.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    #     login_user(user_object)
    #     return redirect(url_for('search'))

    return render_template("login.html", form=login_form)


@app.route("/search", methods=['GET', 'POST'])
def search():
    search = BookSearchForm(request.form)
    if not current_user.is_authenticated:
        return render_template("please_login.html")
    
    if request.method == 'POST':
        return search_results(search)

    return render_template("search.html", form=search)


@app.route('/results', methods=['GET'])
def search_results(search):
    results = []
    search_string = string.capwords(search.data['search'], sep = None)

    if search_string:
        # qry = db_session.query(Book).filter((Book.title.contains(search_string)) | (Book.author.contains(search_string)) | (Book.year.contains(search_string)) | (Book.isbn.contains(search_string)))
        # qry = db.session.query(Book).filter((Book.title.contains(search_string)) | (Book.author.contains(search_string)) | (Book.year.contains(search_string)) | (Book.isbn.contains(search_string)))
        # results = qry.order_by(Book.author.asc()).all()

        results = db.session.execute("SELECT isbn, author, title, year FROM books WHERE isbn iLIKE '%"+search_string+"%' OR author iLIKE '%"+search_string+"%' OR title iLIKE '%"+search_string+"%' OR year iLIKE '%"+search_string+"%' ORDER BY author").fetchall()
        # results = qry.order_by(Book.author.asc()).all() 
          

    else:
        # qry = db_session.query(Book)
        # qry = db.session.query(Book)
        # results = qry.all()
        results = db.session.execute("SELECT * FROM books ORDER BY year")
        
    if not results:
        flash('No results found!')
        return redirect('/search')
    else:
        # display results
        table = Results(results)
        table.border = True
        return render_template('results.html', table=table)

# @app.route('/book', methods=['GET'])
# def display_info():
#     if not current_user.is_authenticated:
#         return render_template("please_login.html")
#     else:
#         return render_template("book.html")

@app.route('/book/<isbn>', methods=['GET'])
def display_info(isbn):
    if not current_user.is_authenticated:
        return render_template("please_login.html")
    else:
        if request.method == 'GET':

            row = db.session.execute("SELECT isbn, title, author, year FROM books WHERE \
                            isbn = :isbn",
                            {"isbn": isbn})
            book_info = row.fetchone()

            """USE GOODREADS API"""

            key = os.getenv('GOODREADS_API_KEY')

            res = requests.get("https://www.goodreads.com/book/review_counts.json", params = {"key" : key, "isbns": isbn})
            if res.status_code != 200:
                return render_template("error.html", message="API request unsuccessful.")
            review_data = res.json()

            return render_template("book.html", book_info = book_info, review_data = review_data)
        



@app.route("/logout", methods=['GET'])
def logout():

    if not current_user.is_authenticated:
        return render_template("please_login.html")

    logout_user()
    return render_template("logout.html")


if __name__ == "__main__":
    app.run(debug=True)