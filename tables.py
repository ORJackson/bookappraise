from flask_table import Table, Col, LinkCol
from models import Book

# Table for displaying search results

class Results(Table):
    classes = ['my_table']
    id = Col('Id', show=False)
    isbn = Col('ISBN')
    title = Col('Title')
    author = Col('Author')
    year = Col('Year')
    more_info = LinkCol('More Info',   url_kwargs=dict(isbn='isbn'), endpoint='display_info')