"""Recreated for reference, CREATE TABLE users executed in terminal"""

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE ,
    PASSWORD VARCHAR NOT NULL, 
    
    -- CONSTRAINT check_username_unique UNIQUE (username)


"""CREATE TABLE books executed in import.py"""
CREATE TABLE books (
    id SERIAL PRIMARY KEY, 
    isbn VARCHAR NOT NULL, 
    title VARCHAR NOT NULL, 
    author VARCHAR NOT NULL, 
    year VARCHAR NOT NULL))

"""CREATE TABLE reviews executed in terminal"""
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    book_id INTEGER REFERENCES books,
    comment VARCHAR NOT NULL,
    rating INTEGER NOT NULL, 
    date DATE NOT NULL,
    CONSTRAINT check_rating_valid CHECK (rating BETWEEN 1 and 5)
)