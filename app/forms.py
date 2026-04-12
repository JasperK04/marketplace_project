from typing import Any, cast

import sqlalchemy as sa
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Regexp,
    ValidationError,
)

from app.extensions import db
from app.models.Category import Category
from app.models.Listing import Listing
from app.models.User import User


def get_categories():
    return [
        (category.name, category.name) for category in db.session.query(Category).all()
    ]


class RegistrationForm(FlaskForm):
    name = StringField(
        "Name",
        render_kw={
            "class": "text",
            "placeholder": "Enter your full name",
            "autocomplete": "name",
            "autofocus": "autofocus",
        },
        validators=[
            DataRequired(),
            Length(1, 70, message="Name must be between 1 and 70 characters long"),
        ],
    )
    username = StringField(
        "Username",
        render_kw={
            "class": "text",
            "placeholder": "Enter a username",
            "autocomplete": "username",
        },
        validators=[
            DataRequired(),
            Regexp(
                r"^[a-zA-Z0-9_.-]{2,}$",
                message='Username must be longer than 2 characters and consist of alphanumeric characters or one of the following: "_.-"',
            ),
        ],
    )
    email = StringField(
        "Email",
        render_kw={
            "class": "text",
            "placeholder": "Enter your email",
            "autocomplete": "email",
        },
        validators=[DataRequired(), Email()],
    )
    password = PasswordField(
        "Password",
        render_kw={
            "class": "text",
            "placeholder": "Enter a password",
            "autocomplete": "new_password",
        },
        validators=[DataRequired(), Length(15, 65)],
    )
    password2 = PasswordField(
        "Repeat Password",
        render_kw={
            "class": "text",
            "placeholder": "Repeat password",
            "autocomplete": "new_password",
        },
        validators=[DataRequired(), EqualTo("password")],
    )
    file = FileField(
        "Upload profile picture",
        render_kw={
            "class": "file-input",
            "onchange": "getFileName(event)",
            "accept": "image/jpeg, image/jpg, image/png",
        },
        validators=[FileAllowed(["jpg", "jpeg", "png"])],
    )
    submit = SubmitField("Register", render_kw={"class": "submit"})

    is_admin = BooleanField(
        "Register as admin",
        render_kw={"class": "checkbox_input"},
        default=False,
    )

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError("Email address already exists.")


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired()],
        render_kw={
            "class": "text",
            "placeholder": "Enter your full name",
            "autocomplete": "username",
            "autofocus": "autofocus",
        },
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={
            "class": "text",
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
        },
    )
    remember_me = BooleanField(render_kw={"class": "checkbox_input"})
    submit = SubmitField("Sign In", render_kw={"class": "submit"})


class ListingForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[DataRequired()],
        render_kw={
            "class": "text",
            "placeholder": "Enter a product title",
            "autocomplete": "no",
            "autofocus": "autofocus",
        },
    )
    category = RadioField(
        "Category", validators=[DataRequired()], render_kw={"class": "radiofield_input"}
    )
    condition = SelectField(
        "Condition", validators=[DataRequired()], render_kw={"class": "text"}
    )
    description = TextAreaField(
        "Description",
        validators=[DataRequired()],
        render_kw={
            "class": "text-area",
            "placeholder": "Enter a product description",
            "autocomplete": "no",
        },
    )
    price = StringField(
        "Price",
        validators=[
            DataRequired(),
            Regexp(
                r"^[0-9]+([.,][0-9]+)*$",
                message="Can only enter numbers or one of the following:,.",
            ),
        ],
        render_kw={"class": "text", "placeholder": "12,34", "autocomplete": "no"},
    )
    file = FileField(
        "Upload image (300x200)",
        validators=[FileAllowed(["jpg", "jpeg", "png"])],
        render_kw={
            "class": "file-input",
            "onchange": "getFileName(event)",
            "accept": "image/jpeg, image/jpg, image/png",
        },
    )
    submit = SubmitField("Submit", render_kw={"class": "submit"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = cast(list[Any], get_categories())
        self.condition.choices = cast(list[Any], Listing.CONDITION_CHOICES)
        if not self.condition.data:
            self.condition.data = Listing.DEFAULT_CONDITION


class EditProfileForm(FlaskForm):
    username = StringField(
        "username",
        validators=[
            DataRequired(),
            Regexp(
                r"^[a-zA-Z0-9_.-]{2,}$",
                message='Username must be longer than 2 characters and consist of alphanumeric characters or one of the following: "_.-"',
            ),
        ],
        render_kw={
            "class": "text",
            "placeholder": "Enter a new username",
            "autocomplete": "username",
            "autofocus": "autofocus",
        },
    )
    about_me = TextAreaField(
        "About Me",
        render_kw={
            "class": "text-area",
            "placeholder": "Talk about yourself",
            "autocomplete": "no",
        },
    )
    file = FileField(
        "Upload (new) profile picture (200x200)",
        validators=[FileAllowed(["jpg", "jpeg", "png"])],
        render_kw={
            "class": "file-input",
            "onchange": "getFileName(event)",
            "accept": "image/jpeg, image/jpg, image/png",
        },
    )
    submit = SubmitField("Save Changes", render_kw={"class": "submit"})

    is_admin = BooleanField(
        "Admin",
        render_kw={"class": "checkbox_input"},
        default=False,
    )


class ToggleAdminForm(FlaskForm):
    submit = SubmitField("Toggle Admin", render_kw={"class": "submit"})
