from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from passlib.hash import pbkdf2_sha256
from models import User

def invalid_credentials(form, field):
    """ This function checks username and password """

    username_entered = form.username.data
    password_entered = field.data

    #check if username exists and the password matches
    user_object = User.query.filter_by(username=username_entered).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif not pbkdf2_sha256.verify(password_entered, user_object.password):
        raise ValidationError("Username or password is incorrect")


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
        
class LoginForm(FlaskForm):
    """ Login Form """
    username = StringField('username_label', validators=[InputRequired(message="Username required")])
    password = PasswordField('password_label', validators=[InputRequired(message="Password required"), invalid_credentials])
    submit_button = SubmitField('Login')