from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
import sqlalchemy as sa
from app.extensions import db
from app.models.User import User

class RegistrationForm(FlaskForm):
    name = StringField('Name', render_kw={"class": "text", "placeholder": "Enter your full name", "autocomplete": "name", "autofocus": "autofocus"},
                       validators=[DataRequired(),Length(1, 70, message='Name must be between 1 and 70 characters long')])
    username = StringField('Username', render_kw={"class": "text", "placeholder": "Enter a username", "autocomplete": "username"}, validators=[DataRequired(),
                           Regexp(r"^[a-zA-Z0-9_.-]{2,}$", message='Username must be longer than 2 characters and consist of alphanumeric characters or one of the following: "_.-"')])
    email = StringField('Email', render_kw={"class": "text", "placeholder": "Enter your email", "autocomplete": "email"},
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', render_kw={"class": "text", "placeholder": "Enter a password", "autocomplete": "new_password"},
                             validators=[DataRequired(),Length(15,65)])
    password2 = PasswordField('Repeat Password', render_kw={"class": "text", "placeholder": "Repeat password", "autocomplete": "new_password"},
                              validators=[DataRequired(), EqualTo('password')])
    file = FileField('Upload profile picture', render_kw={"class": "file-input", "onchange": "getFileName(event)", "accept": "image/jpeg, image/jpg, image/png"},
                     validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Register', render_kw={"class": "submit"})

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Email address already exists.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()],
                           render_kw={"class": "text", "placeholder": "Enter your full name", "autocomplete": "username", "autofocus": "autofocus"})
    password = PasswordField('Password', validators=[DataRequired()],
                             render_kw={"class": "text", "placeholder": "Enter your password", "autocomplete": "current-password"})
    remember_me = BooleanField(render_kw={"class": "checkbox_input"})
    submit = SubmitField('Sign In', render_kw={"class": "submit"})


class ListingForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    category = RadioField('Category', validators=[DataRequired()])
    description = TextAreaField('Description',validators=[DataRequired()])
    price = StringField('Price',validators=[DataRequired(),Regexp(r"^[0-9]+([.,][0-9]+)*$",message="Can only enter numbers or one of the following:,.")])
    file = FileField('Upload image (300x200)',validators=[FileAllowed(['jpg', 'jpeg','png'])])
    submit = SubmitField('Submit', render_kw={"class": "submit"})


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(),Length(1, 70, message='Name must be between 1 and 70 characters long')])
    about_me = TextAreaField('About Me')
    file = FileField('Upload (new) profile picture (200x200)',validators=[FileAllowed(['jpg', 'jpeg','png'])])
    submit = SubmitField('Save Changes', render_kw={"class": "submit"})
