import os
from flask import Flask, session, render_template, redirect, url_for, request, flash, jsonify
from flask_session import Session
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

# Configure database 
app.config['SQLALCHEMY_DATABASE_URI']= os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
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
    if current_user.is_authenticated:
        return redirect(url_for('search'))
    else:

        reg_form = RegistrationForm()

        #if the validation is successful updates the database
        if reg_form.validate_on_submit():
            username = reg_form.username.data
            password = reg_form.password.data

            #Hash password
            hashed_password = pbkdf2_sha256.hash(password)

            db.session.execute("INSERT INTO users (username, password) VALUES (:username, :password)",\
                {"username": username, "password" : hashed_password})
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
        results = db.session.execute("SELECT isbn, author, title, year FROM books \
            WHERE isbn iLIKE '%"+search_string+"%' OR author iLIKE '%"+search_string+"%'\
                 OR title iLIKE '%"+search_string+"%' OR year iLIKE '%"+search_string+"%'\
                      ORDER BY author").fetchall()

    else:
        results = db.session.execute("SELECT * FROM books ORDER BY year")
        
    if not results:
        flash('No results found!')
        return redirect('/search')
    else:
        # display results
        table = Results(results)
        table.border = True
        return render_template('results.html', table=table)

@app.route('/book/<isbn>', methods=['GET', 'POST'])
def display_info(isbn):
    review = BookReviewForm(request.form)
    book_row = db.session.execute("SELECT id FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    book_id = book_row['id']

    if not current_user.is_authenticated:
        return render_template("please_login.html")
    else:
        if request.method == 'GET':
            row = db.session.execute("SELECT isbn, title, author, year FROM books WHERE \
                            isbn = :isbn",
                            {"isbn": isbn})
            book_info = row.fetchone()

            """USE GOODREADS API to get average rating and rating count"""

            key = os.getenv('GOODREADS_API_KEY')
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params = {"key" : key, "isbns": isbn})

            if res.status_code != 200:
                return render_template("error.html", message="API request unsuccessful.")
            review_data = res.json()

            """Query database for user reviews"""

            user_reviews = db.session.execute("SELECT users.username, comment, rating, date FROM reviews \
                INNER JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id ORDER BY date DESC", \
                    {"book_id": book_id}).fetchall()
            return render_template("book.html", book_info = book_info, review_data = review_data, res = res, form = review, user_reviews = user_reviews)

        """Post a review"""

        if request.method == 'POST':
            
            user_id = current_user.id
            comment = review.data['review']
            rating = review.data['rating']

            """Search for existing review by this user on this book"""

            existing_review = db.session.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",\
                 {"user_id": user_id, "book_id": book_id}).fetchone()

            if existing_review:
                flash('You cannot review the same book twice.')
                return redirect('/book/' + isbn)

            else:
            
                """If no review of this book exists from this user, post review"""

                db.session.execute("INSERT INTO reviews (user_id, book_id, comment, rating, date) VALUES (:user_id, :book_id, :comment, :rating, CURRENT_DATE)", \
                    {"user_id" : user_id, "book_id" : book_id, "comment" : comment, "rating" : rating})
                db.session.commit()
                flash('Thanks for the review!')
                return redirect('/book/' + isbn)

@app.route('/api/<isbn>', methods=['GET'])
def display_book_json(isbn):

    if not current_user.is_authenticated:
        return render_template("please_login.html")
    else:
            """Display book info and bookAPPraise review data as a json"""
            
            book_query = db.session.execute("SELECT books.title, books.author, books.year, books.isbn, \
                COUNT(reviews.comment) AS review_count, ROUND(AVG(reviews.rating), 2) AS average_score \
                    FROM reviews INNER JOIN books ON reviews.book_id = books.id WHERE books.isbn = :isbn \
                        GROUP BY title, author, year, isbn", {"isbn": isbn}).fetchone()
            
            if book_query:
                book_dict = dict(book_query)
                book_dict['average_score'] = float(book_dict['average_score'])
                book_json = jsonify(book_dict)
                return book_json

            else:
                return render_template("error.html", message="404. Uh oh! No results found. We have no review data for that book.")

@app.route("/logout", methods=['GET'])
def logout():

    if not current_user.is_authenticated:
        return render_template("please_login.html")

    logout_user()
    return render_template("logout.html")

if __name__ == "__main__":
    app.run(debug=True)
    session.permanent = False