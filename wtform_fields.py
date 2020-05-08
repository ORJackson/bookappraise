from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField("username_label", validators=[InputRequired(message="Username required"), Length(min=4, max=20, message="Username must be between 4 and 20 characters")])
    password = PasswordField("password_label", validators=[InputRequired(message="Password required")])
    confirm_password = PasswordField("confirm_password_label", validators=[InputRequired(message="Password required"), EqualTo('password', message="Passwords must match")])
    submit_button = SubmitField('Register')

#Query database to check if another user has taken a specific username
    def validate_username(self, username): 
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists. Select a different username.")
        
