import os
from random import choice, randint
from typing import cast

import click
import sqlalchemy as sa
from faker import Faker
from flask import Blueprint, current_app

from app.extensions import db
from app.models.Category import Category
from app.models.Listing import Listing
from app.models.User import User
from app.route_utils import resize_upload_image

cli = Blueprint("cli", __name__)


@cli.cli.command("recreate-db")
@click.option("--users", type=int, default=50, help="Number of users to create.")
@click.option("--listings", type=int, default=200, help="Number of listings to create.")
def initialize_database(users: int, listings: int):
    """Drops the current database and creates a new one with faked data."""
    fake = Faker()
    categories: dict[str, dict[str, list[str] | str]] = {
        "Electronics": {
            "keywords": [
                "smartphone",
                "laptop",
                "tablet",
                "headphones",
                "camera",
                "smartwatch",
                "monitor",
                "printer",
                "router",
                "speaker",
            ],
            "description": "Electronic devices and gadgets.",
            "path": "static/assets/images/electronics.jpeg",
        },
        "Clothing": {
            "keywords": [
                "t-shirt",
                "jeans",
                "jacket",
                "dress",
                "shoes",
                "hat",
                "scarf",
                "socks",
                "blouse",
                "suit",
            ],
            "description": "Apparel and accessories.",
            "path": "static/assets/images/clothes.jpeg",
        },
        "Books": {
            "keywords": [
                "novel",
                "cookbook",
                "biography",
                "textbook",
                "poetry collection",
                "graphic novel",
                "dictionary",
                "manual",
                "guidebook",
                "memoir",
            ],
            "description": "Literature and educational materials.",
            "path": "static/assets/images/books.jpeg",
        },
        "Home & Garden": {
            "keywords": [
                "sofa",
                "table",
                "chair",
                "lamp",
                "rug",
                "blender",
                "microwave",
                "garden tools",
                "plant pot",
                "shelf",
            ],
            "description": "Furniture and home improvement items.",
            "path": "static/assets/images/home.jpeg",
        },
        "Fashion & Beauty": {
            "keywords": [
                "lipstick",
                "perfume",
                "makeup kit",
                "nail polish",
                "handbag",
                "watch",
                "sunglasses",
                "skincare set",
                "bracelet",
                "necklace",
            ],
            "description": "Beauty products and fashion accessories.",
            "path": "static/assets/images/fashion.jpeg",
        },
        "Sport": {
            "keywords": [
                "soccer ball",
                "basketball",
                "tennis racket",
                "yoga mat",
                "helmet",
                "bicycle",
                "weights",
                "swimsuit",
                "golf club",
                "sneakers",
            ],
            "description": "Sporting goods and fitness equipment.",
            "path": "static/assets/images/sport.jpeg",
        },
        "Toys": {
            "keywords": [
                "action figure",
                "doll",
                "lego set",
                "board game",
                "puzzle",
                "plush toy",
                "toy car",
                "building blocks",
                "playset",
                "remote control car",
            ],
            "description": "Children's toys and games.",
            "path": "static/assets/images/toys.jpeg",
        },
        "Vehicles": {
            "keywords": [
                "car",
                "motorcycle",
                "bicycle",
                "scooter",
                "truck",
                "boat",
                "trailer",
                "camper",
                "ATV",
                "skateboard",
            ],
            "description": "Various types of vehicles and related accessories.",
            "path": "static/assets/images/vehicles.jpeg",
        },
        "Music": {
            "keywords": [
                "guitar",
                "piano",
                "violin",
                "drum set",
                "microphone",
                "amplifier",
                "headphones",
                "record player",
                "flute",
                "trumpet",
            ],
            "description": "Musical instruments and audio equipment.",
            "path": "static/assets/images/music.jpeg",
        },
        "Other": {
            "keywords": [
                "antique",
                "art piece",
                "collectible",
                "instrument",
                "tool",
                "pet supplies",
                "hobby kit",
                "gift card",
                "novelty item",
                "unknown item",
            ],
            "description": "Miscellaneous items that do not fit into other categories.",
            "path": "static/assets/images/other.jpeg",
        },
    }
    adjectives = [
        "smart",
        "fast",
        "reliable",
        "durable",
        "stylish",
        "modern",
        "classic",
        "unique",
        "rare",
        "vintage",
    ]
    session_dir = current_app.config.get("SESSION_FILE_DIR") or os.path.abspath(
        "flask_session"
    )
    if os.path.exists(session_dir):
        for filename in os.listdir(session_dir):
            filepath = os.path.join(session_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        print("Sessions cleared.")

    db.drop_all()
    print("Database dropped.")
    db.create_all()
    print("Database created.")
    for category, category_data in categories.items():
        description = cast(str, category_data["description"])
        db.session.add(
            Category().from_dict({"name": category, "description": description})
        )
    db.session.commit()
    print("Categories created.")
    new_users: list[User] = []
    while len(new_users) < users:
        name = fake.name()
        username = name.lower().replace(" ", "")
        new_user = User().from_dict(
            {
                "username": username,
                "name": name,
                "email": fake.email(),
                "password": fake.password(length=randint(15, 65)),
            },
            new_user=True,
        )
        if new_user.email not in [
            user.email for user in new_users
        ] and new_user.username not in [user.username for user in new_users]:
            new_users.append(new_user)
    for new_user in new_users:
        db.session.add(new_user)

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_name = os.getenv("ADMIN_NAME")
    admin_email = os.getenv("ADMIN_EMAIL", fake.email())
    admin_password = os.getenv("ADMIN_PASSWORD")
    if all([admin_username, admin_name, admin_email, admin_password]):
        admin_username = cast(str, admin_username)
        admin_name = cast(str, admin_name)
        admin_email = cast(str, admin_email)
        admin_password = cast(str, admin_password)
        admin = (
            User()
            .from_dict(
                {
                    "username": admin_username,
                    "name": admin_name,
                    "email": admin_email,
                    "password": admin_password,
                },
                new_user=True,
            )
            .make_admin()
        )
        db.session.add(admin)
    else:
        print("Admin creation skipped: ADMIN_* env values are incomplete.")

    db.session.commit()
    print("Users created.")

    created_categories: list[Category] = Category.query.all()
    created_users: list[User] = User.query.all()

    for _ in range(listings):
        category = choice(created_categories)
        product = choice(categories[category.name]["keywords"])
        title = f"{choice(adjectives).capitalize()} {product.capitalize()}"
        description = f"{fake.sentence(nb_words=3)} This {product} is {fake.text(max_nb_chars=50).lower()} and perfect for anyone looking to upgrade their {category.name.lower()}."
        user_id = choice(created_users).id
        condition = choice([key for key, _label in Listing.CONDITION_CHOICES])
        new_listing = Listing().from_dict(
            {
                "title": title,
                "description": description,
                "price": fake.random_int(min=50, max=10000),
                "categoryID": category.id,
                "userID": user_id,
                "condition": condition,
            }
        )

        db.session.add(new_listing)
        db.session.flush()
        file = (
            "app/static/assets/images/"
            + category.name.split(" ", -1)[0].lower()
            + ".png"
        )
        db.session.add(
            resize_upload_image(
                file=file, ratio=(3, 2), size=(600, 400), listing_id=new_listing.id
            )
        )
    db.session.commit()
    print("Listings created.")

    print("Database initialized.")


@cli.cli.command("create-admin")
@click.option(
    "--username",
    type=str,
    default=os.getenv("ADMIN_USERNAME"),
    prompt=os.getenv("ADMIN_USERNAME") is None,
    help="Admin username.",
)
@click.option(
    "--name",
    type=str,
    default=os.getenv("ADMIN_NAME"),
    prompt=os.getenv("ADMIN_NAME") is None,
    help="Admin name.",
)
@click.option(
    "--email",
    type=str,
    default=os.getenv("ADMIN_EMAIL"),
    prompt=os.getenv("ADMIN_EMAIL") is None,
    help="Admin email.",
)
@click.option(
    "--password",
    type=str,
    default=os.getenv("ADMIN_PASSWORD"),
    prompt=os.getenv("ADMIN_PASSWORD") is None,
    help="Admin password.",
)
def create_admin(username: str, name: str, email: str, password: str):
    if not User.valid_username(username):
        print(
            "Username does not meet requirements.\nUsername must only contain alpha-numeric characters."
        )
        return
    if db.session.scalar(sa.select(User).where(User.username == username)):
        print("Username already in use.")
        return
    if len(name) > 70 or len(name) < 1:
        print(
            "Name does not meet requirements.\nName must be between 1 and 70 characters."
        )
        return
    if not User.valid_email(email):
        print("This is not a valid email address.")
        return
    if db.session.scalar(sa.select(User).where(User.email == email)):
        print("Email address already in use.")
        return
    if not User.valid_password(password):
        print(
            "Password does not meet requirements\nPassword must be between 15 and 64 characters long."
        )
        return
    admin = (
        User()
        .from_dict(
            {"username": username, "name": name, "email": email, "password": password},
            new_user=True,
        )
        .make_admin()
    )
    db.session.add(admin)
    db.session.commit()
    print(
        "Admin created with id:",
        admin.id,
        "username:",
        username,
        "name:",
        admin.name,
        "email:",
        admin.email,
        "password:",
        password,
    )
