from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed,FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
import sqlalchemy as sa
from app import db
from app.models.User import User
from app.models.Category import Category

class RegistrationForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired(),Regexp(r"^[a-zA-Z0-9_.-]{2,}$",message='Username must be longer than 2 characters and consist of alphanumeric characters or one of the following: "_.-"')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(15,65)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, name):
        user = db.session.scalar(sa.select(User).where(
            User.name == name.data))
        if user is not None:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Email address already exists.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ListingForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    category = SelectField('Category', choices=[category.name for category in db.session.query(Category).all()], validators=[DataRequired()])
    description = TextAreaField('Description',validators=[DataRequired()])
    price = FloatField('Price',validators=[DataRequired()])
    file = FileField('Upload image',validators=[FileRequired(),FileAllowed(['jpg', 'jpeg','png', 'gif', 'svg'])])
    submit = SubmitField('Add listing')