import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# use dotenv to access DATABASE_URL
from dotenv import load_dotenv
load_dotenv()

# To execute this file run "python3 import.py" from the CLI
# the main() function will create a new database table (books), open the books.csv file, and import data 
# from the csv file to the new "books" table

# create database engine object connecting to the database
engine = create_engine(os.getenv("DATABASE_URL"))

# create a scoped session so that when users interact with the database they are kept separate
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL)")

    with open('books.csv', mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        # next() will skip the first line, which contains headers
        next(csv_reader) 

        for isbn, title, author, year in csv_reader:
            db.execute(
                "INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", 
                {"isbn": isbn, "title": title, "author": author, "year": year},
            )
            # Just for fun...
            print(f"Added book {title} to database.")
        db.commit()

if __name__ == "__main__":
    main()