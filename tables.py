from flask_table import Table, Col, LinkCol
from models import Book

# Table for displaying search results

class Results(Table):
    id = Col('Id', show=False)
    isbn = Col('ISBN')
    # isbn = LinkCol('ISBN', endpoint='display_info', attr=(Book.isbn))
    # isbn = LinkCol('ISBN', endpoint='display_info', url_kwargs=dict(id='id'), anchor_attrs={Book.isbn})
    title = Col('Title')
    author = Col('Author')
    year = Col('Year')
    more_info = LinkCol('More Info',   url_kwargs=dict(isbn='isbn'), endpoint='display_info')