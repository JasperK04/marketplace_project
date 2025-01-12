import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models.User import User

class RegistrationForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, name):
        user = db.session.scalar(sa.select(User).where(
            User.name == name.data))
        if user is not None:
            raise ValidationError('Please use a different username.')
        if re.match(r"^[a-zA-Z0-9_.-]{2,}$", name) is None:
            raise ValidationError('Please use a username that is longer than 2 characters and only consists of alphabetic characters, numbers, or one of the following: "_.-"')


    # Already done automatically by the Email() validator 
    # in wtforms.validators if I understand correctly.
    # pip install email_validator

    #@staticmethod
    #def valid_email(email): # See https://stackoverflow.com/a/201378
    #    return re.match(r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])", email) is not None

    def validate_email(self, email):
        user = db.sessions.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')


    def validate_password(self, password): # See https://pages.nist.gov/800-63-4/sp800-63b.html#passwordver 
        if 15 <= len(password) <= 64:
            raise ValidationError('Please use a password that is between 15 and 64 characters long.')
        if not password.strip():
            raise ValidationError('Please use a different password.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')