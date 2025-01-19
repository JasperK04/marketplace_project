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
@click.option("--users", type=int, default=50, help="Number of users to create.")
@click.option("--listings", type=int, default=500, help="Number of listings to create.")
def initialize_database(users: int, listings: int):
    """Drops the current database and creates a new one with faked data."""
    fake = Faker()
    categories: dict[str, dict[str, list[str] | str]] = {
        "Electronics": {'keywords': ["smartphone", "laptop", "tablet", "headphones", "camera", "smartwatch", "monitor", "printer", "router", "speaker"], 'description': "Electronic devices and gadgets."},
        "Clothing": {"keywords": ["t-shirt", "jeans", "jacket", "dress", "shoes", "hat", "scarf", "socks", "blouse", "suit"], 'description': "Apparel and accessories."},
        "Books": {"keywords": ["novel", "cookbook", "biography", "textbook", "poetry collection", "graphic novel", "dictionary", "manual", "guidebook", "memoir"], 'description': "Literature and educational materials."},
        "Home & Garden": {"keywords": ["sofa", "table", "chair", "lamp", "rug", "blender", "microwave", "garden tools", "plant pot", "shelf"], 'description': "Furniture and home improvement items."},
        "Fashion & Beauty": {"keywords": ["lipstick", "perfume", "makeup kit", "nail polish", "handbag", "watch", "sunglasses", "skincare set", "bracelet", "necklace"], 'description': "Beauty products and fashion accessories."},
        "Sport": {"keywords": ["soccer ball", "basketball", "tennis racket", "yoga mat", "helmet", "bicycle", "weights", "swimsuit", "golf club", "sneakers"], 'description': "Sporting goods and fitness equipment."},
        "Toys": {"keywords": ["action figure", "doll", "lego set", "board game", "puzzle", "plush toy", "toy car", "building blocks", "playset", "remote control car"], 'description': "Children's toys and games."},
        "Vehicles": {"keywords": ["car", "motorcycle", "bicycle", "scooter", "truck", "boat", "trailer", "camper", "ATV", "skateboard"], 'description': "Various types of vehicles and related accessories."},
        "Other": {"keywords": ["antique", "art piece", "collectible", "instrument", "tool", "pet supplies", "hobby kit", "gift card", "novelty item", "unknown item"], 'description': "Miscellaneous items that do not fit into other categories."},
    }
    adjectives = ["smart", "fast", "reliable", "durable", "stylish", "modern", "classic", "unique", "rare", "vintage"]
    db.drop_all()
    print("Database dropped.")
    db.create_all()
    print("Database created.")
    for category, category_data in categories.items():
        db.session.add(Category().from_dict({"name": category, "description": category_data['description']}))
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
        if new_user.email not in [user.email for user in new_users] and new_user.username not in [user.username for user in new_users]:
            new_users.append(new_user)
    for new_user in new_users:
        db.session.add(new_user)


    db.session.commit()
    print("Users created.")

    created_categories: list[Category] = Category.query.all()
    created_users: list[User] = User.query.all()

    for _ in range(listings):
        category = choice(created_categories)
        product = choice(categories[category.name]["keywords"])
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


@cli.cli.command("create-admin")
@click.option("--name", type=str, prompt="Name", help="Admin name.")
@click.option("--email", type=str, prompt="Email", help="Admin email.")
@click.option("--password", type=str, prompt="Password", help="Admin password.")
def create_admin(name:str, email:str, password:str):
    if not User.valid_name(name):
        print("Invalid username. Username must only contain alpha-numeric characters.")
        return
    if not User.valid_email(email):
        print("Invalid email address.")
        return
    if db.session.scalar(User.query.filter(User.email == email)):
        print("Email address already in use.")
        return
    if not User.valid_password(password):
        print("Invalid password. Password must be between 15 and 64 characters long.")
        return
    admin = User().from_dict({"name": name, "email": email, "password": password}, new_user=True).make_admin()
    db.session.add(admin)
    db.session.commit()
    print("Admin created with id:", admin.id, "name:", admin.name, "email:", admin.email, "password:", password)
