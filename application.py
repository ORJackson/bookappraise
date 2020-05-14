import os

from flask import Flask, session, render_template, redirect, url_for, request, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import LoginManager, login_user, current_user, logout_user

from wtform_fields import *
from models import *

# secret_key and database info stored in .env
# Configure app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', None)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI']= os.getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)

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
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():

    login_form = LoginForm()

    #Allow login if validation is successful
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

# from: https://www.blog.pythonlibrary.org/2017/12/13/flask-101-how-to-add-a-search-form/
# Not sure about this....
@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
    if search.data['search'] == '':
        qry = db_session.query(Book)
        results = qry.all()
    if not results:
        flash('No results found!')
        return redirect('/search')
    else:
        # display results
        return render_template('results.html', results=results)



@app.route("/logout", methods=['GET'])
def logout():

    if not current_user.is_authenticated:
        return render_template("please_login.html")

    logout_user()
    return render_template("logout.html")


# @app.route("/<string:name>")
# def hello(name):
#     name = name.capitalize()
#     return f"Hello, {name}!"

if __name__ == "__main__":
    app.run(debug=True)