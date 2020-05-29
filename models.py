from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """ User model """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String)
    title = db.Column(db.String)
    author = db.Column(db.String)
    year = db.Column(db.String)

# class Review(db.Model):
#     """ Review Model """

#     __tablename__ = "reviews"

#     id = db.Column(db.Integer, primary_key=True)
#     review = db.Column(db.String, nullable=False)
#     rating = db.Column(db.Integer, nullable=False)
#     user_id = db.Column(db.Integer, ForeignKey('public.users.id'), nullable=False)
#     book_id = db.Column(db.Integer, ForeignKey('public.books.id'), nullable=False)