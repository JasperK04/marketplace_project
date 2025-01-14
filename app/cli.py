from random import randint, choice
from flask import Blueprint
import click
from faker import Faker
from app import db
from app.models.User import User
from app.models.Listing import Listing
from app.models.Category import Category

cli = Blueprint("cli", __name__)


@cli.cli.command("recreate-db")
@click.option("--users", type=int, default=10, help="Number of users to create.")
@click.option("--listings", type=int, default=100, help="Number of listings to create.")
def initialize_database(users: int, listings: int):
    """Drops the current database and creates a new one with faked data."""
    fake = Faker()
    categories = {
        "Electronics": ["smartphone", "laptop", "tablet", "headphones", "camera", "smartwatch", "monitor", "printer", "router", "speaker"],
        "Clothing": ["t-shirt", "jeans", "jacket", "dress", "shoes", "hat", "scarf", "socks", "blouse", "suit"],
        "Books": ["novel", "cookbook", "biography", "textbook", "poetry collection", "graphic novel", "dictionary", "manual", "guidebook", "memoir"],
        "Home & Garden": ["sofa", "table", "chair", "lamp", "rug", "blender", "microwave", "garden tools", "plant pot", "shelf"],
        "Fashion & Beauty": ["lipstick", "perfume", "makeup kit", "nail polish", "handbag", "watch", "sunglasses", "skincare set", "bracelet", "necklace"],
        "Sport": ["soccer ball", "basketball", "tennis racket", "yoga mat", "helmet", "bicycle", "weights", "swimsuit", "golf club", "sneakers"],
        "Toys": ["action figure", "doll", "lego set", "board game", "puzzle", "plush toy", "toy car", "building blocks", "playset", "remote control car"],
        "Vehicles": ["car", "motorcycle", "bicycle", "scooter", "truck", "boat", "trailer", "camper", "ATV", "skateboard"],
        "Other": ["antique", "art piece", "collectible", "instrument", "tool", "pet supplies", "hobby kit", "gift card", "novelty item", "unknown item"],
    }
    adjectives = ["smart", "fast", "reliable", "durable", "stylish", "modern", "classic", "unique", "rare", "vintage"]
    db.drop_all()
    print("Database dropped.")
    db.create_all()
    print("Database created.")
    for category in categories.keys():
        db.session.add(Category().from_dict({"name": category}))
    db.session.commit()
    print("Categories created.")
    for _ in range(users):
        db.session.add(
            User()
            .from_dict(
                {
                    "name": fake.user_name(),
                    "email": fake.email(),
                    "password": fake.password(length=randint(15, 65)),
                },
                new_user=True,
            )
        )

    db.session.commit()
    print("Users created.")

    created_categories: list[Category] = Category.query.all()
    created_users: list[User] = User.query.all()

    for _ in range(listings):
        category = choice(created_categories)
        product = choice(categories[category.name])
        title = f"{choice(adjectives).capitalize()} {product.capitalize()}"
        description = f"{fake.sentence(nb_words=3)} This {product} is {fake.text(max_nb_chars=50).lower()} and perfect for anyone looking to upgrade their {category.name.lower()}."

        db.session.add(
            Listing().from_dict(
                {
                    "title": title,
                    "description": description,
                    "price": fake.random_int(min=50, max=10000),
                    "categoryID": category.id,
                    "userID": choice(created_users).id,
                }
            )
        )

    db.session.commit()
    print("Listings created.")

    print("Database initialized.")


@cli.cli.command("test")
def test():
    print("Test command executed.")
