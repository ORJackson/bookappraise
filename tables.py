from flask_table import Table, Col

class Results(Table):
    id = Col('Id', show=False)
    isbn = Col('ISBN')
    title = Col('Title')
    author = Col('Author')
    year = Col('Year')
    