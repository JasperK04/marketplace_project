from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from sqlalchemy import select
from urllib.parse import urlsplit
import os


from app.extensions import db
from app.config import config
from app.forms import LoginForm, RegistrationForm, ListingForm, EditProfileForm
from app.models.User import User
from app.models.Listing import Listing
from app.models.Category import Category
from app.models.Image import Image
from app.route_utils import get_open_listings_with_images, resize_upload_image, delete_images

app_config = config[os.getenv("FLASK_ENV", "development")]

routes = Blueprint("routes", __name__)


def can_view_restricted_pages():
    return current_user.is_authenticated and current_user.is_admin


@routes.route("/", methods=["GET"])
@routes.route("/index", methods=["GET"])
def index():
    listings = get_open_listings_with_images(limit=30)

    categories = db.session.query(
        Category
    ).all()  # pylint: disable=redefined-outer-name
    return render_template("index.html", listings=listings, categories=categories)


@routes.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("routes.login"))
        if user.is_deactivated:
            flash("Account is deactivated")
            return redirect(url_for("routes.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("routes.index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@routes.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("routes.login"))


@routes.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.session.scalar(sa.select(User).where(User.name == form.username.data)):
            flash("Username already taken")
            return redirect(url_for("register"))
        if db.session.scalar(sa.select(User).where(User.email == form.email.data)):
            flash("Email address already exists.")
            return redirect(url_for("register"))
        user = User().from_dict(
            {
                "username": form.username.data,
                "name": form.name.data,
                "email": form.email.data,
                "password": form.password.data,
            },
            new_user=True,
        )
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("routes.login"))
    return render_template("register.html", title="Register", form=form)


# Profile stuff
@routes.route("/profile/<user_name>", methods=["GET"])
def profile_by_name(user_name:str):
    print(user_name)
    user = db.session.scalar(select(User).where(User.username == user_name))
    if not user:
        return redirect(url_for('index'))
    if user.is_deactivated and not can_view_restricted_pages():
        return redirect(url_for('index'))
    listings = get_open_listings_with_images(by_user=user.id)
    # Will get this sorted out later, hopefully
    # profile_pic = db.session.execute(
    #    sa.select(Image).where(Image.userID == user.id)).scalars()
    return render_template("profile.html", user=user, listings=listings)

@routes.route("/profile/<int:user_id>", methods=["GET"])
def profile(user_id:int):
    user = db.get_or_404(User, user_id)
    if user.is_deactivated and not can_view_restricted_pages():
        return redirect(url_for("routes.index"))
    listings = get_open_listings_with_images(by_user=user_id)
    # Will get this sorted out later, hopefully
    # profile_pic = db.session.execute(
    #    sa.select(Image).where(Image.userID == user.id)).scalars()
    return render_template("profile.html", user=user, listings=listings)


@routes.route("/profile/<user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(user_id):
    user = db.get_or_404(User, user_id)
    listings = get_open_listings_with_images(by_user=user_id)

    if user.id != current_user.id:
        flash("You are not allowed to edit this profile.")
        return render_template("profile.html", user=user, listings=listings)

    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        user.about_me = form.about_me.data
        user.name = form.name.data
        db.session.add(user)
        db.session.commit()
        return render_template("profile.html", user=user, listings=listings)

    return render_template("edit_profile.html", user=user, form=form)


# Listings
@routes.route("/listings", methods=["GET"])
def listings():
    listings = get_open_listings_with_images()
    return render_template("listings.html", listings=listings)


@routes.route("/listings/<int:listing_id>", methods=["GET"])
def listing(listing_id: int):
    listing = db.get_or_404(Listing, listing_id).to_dict()
    image = db.session.execute(
        sa.select(Image).where(
            (Image.listingID == listing_id) & (Image.variant == "resized")
        )
    ).scalar()
    if image:
        listing["filename"] = image.filename
    if listing["is_deactivated"] and not can_view_restricted_pages():
        return redirect(url_for("routes.listings"))
    return render_template("listing.html", listing=listing)


@routes.route("/add_listing", methods=["GET", "POST"])
@login_required
def add_listing():
    form = ListingForm()
    form.category.choices = [
        category.name for category in db.session.query(Category).all()
    ]
    form.submit.label.text = "Add listing"
    if form.validate_on_submit():
        file = request.files.get("file")
        cat_id = db.session.scalar(
            select(Category.id).where(Category.name == form.category.data)
        )

        new_listing = Listing().from_dict(
            {
                "title": Listing.normalize_title(form.title.data),
                "categoryID": cat_id,
                "description": Listing.normalize_description(form.description.data),
                "price": Listing.normalize_price(form.price.data),
                "userID": current_user.id,
            },
            sold=False,
        )
        db.session.add(new_listing)
        db.session.flush()
        if file:
            img_org = resize_upload_image(file,(300,200),current_user.id,new_listing.id,'UPLOAD_FOLDER','listing','original')
            img_resized = resize_upload_image(file,(600,400),current_user.id,new_listing.id,'RESIZED_FOLDER','listing','resized')
            db.session.add(img_org)
            db.session.add(img_resized)
        db.session.commit()
        return redirect(url_for("routes.index"))
    return render_template("add_listing.html", title="Add listing", form=form)


@routes.route("/edit/<int:listing_id>", methods=["GET", "POST"])
@login_required
def edit_listing(listing_id:int):
    listing = db.get_or_404(Listing, listing_id)

    if listing.userID != current_user.id:
        flash("You are not allowed to edit this listing.")
        return redirect(
            url_for("routes.index")
        )  # this depends on where the edit button/link will be placed

    form = ListingForm(obj=listing)  # so that form is prefilled (only category is not)
    form.category.choices = [
        category.name for category in db.session.query(Category).all()
    ]
    form.submit.label.text = "Edit listing"
    if form.validate_on_submit():
        file = request.files["file"]
        if file:
            # delete old images on disk and in the database
            delete_images(listing_id)

            # add new ones
            img_org = resize_upload_image(
                file,
                (300, 200),
                current_user.id,
                listing_id,
                "UPLOAD_FOLDER",
                "listing",
                "original",
            )
            img_resized = resize_upload_image(
                file,
                (600, 400),
                current_user.id,
                listing_id,
                "RESIZED_FOLDER",
                "listing",
                "resized",
            )

            db.session.add(img_org)
            db.session.add(img_resized)
            db.session.commit()
        listing.title = Listing.normalize_title(form.title.data)
        listing.categoryID = db.session.scalar(
            select(Category.id).where(Category.name == form.category.data)
        )
        listing.description = Listing.normalize_description(form.description.data)
        listing.price = Listing.normalize_price(form.price.data)
        db.session.add(listing)
        db.session.commit()
        return redirect(
            url_for("routes.profile", user_id=current_user.id)
        )  # this depends on where the edit button/link will be placed
    return render_template("add_listing.html", title="Edit listing", form=form)


@routes.route("/delete_listing/<int:listing_id>", methods=["GET", "POST"])
@login_required
def delete_listing(listing_id:int):
    listing = db.get_or_404(Listing, listing_id)

    if listing.userID != current_user.id:
        flash("You are not allowed to delete this listing.")
        return redirect(
            url_for("routes.index")
        )  # this depends on where the edit button/link will be placed

    delete_images(listing_id)

    db.session.delete(listing)
    db.session.commit()
    return redirect(
        url_for("routes.profile", user_id=current_user.id)
    )  # this depends on where the edit button/link will be placed


# Categories
@routes.route("/categories", methods=["GET"])
def categories():
    db_categories = db.session.query(Category).all()
    categories = {
        category.id: {"category": category, "listings": []}
        for category in db_categories
    }
    # get 10 most recent listings for each category, in a single query
    for category_id, value in categories.items():
        value["listings"] = [
            listing.to_dict()
            for listing in db.session.query(Listing)
            .filter_by(categoryID=category_id)
            .order_by(Listing.id.desc())
            .limit(12)
            .all()
        ]
    return render_template("categories.html", categories=categories)


@routes.route("/categories/<int:category_id>", methods=["GET"])
def category(category_id: int):
    category = db.get_or_404(
        Category, category_id
    )  # pylint: disable=redefined-outer-name
    listings = db.session.execute(  # pylint: disable=redefined-outer-name
        sa.select(Listing).where(Listing.categoryID == category.id)
    ).scalars()
    return render_template("category.html", category=category, listings=listings)


@routes.route("/categories/<category_name>", methods=["GET"])
def category_name(category_name: str):  # pylint: disable=redefined-outer-name
    category = db.session.scalar(
        select(Category).where(Category.name == category_name.title())
    )  # pylint: disable=redefined-outer-name
    if category is None:
        return redirect(url_for("routes.index"))
    listings = db.session.execute(  # pylint: disable=redefined-outer-name
        sa.select(Listing).where(Listing.categoryID == category.id)
    ).scalars()
    return render_template("category.html", category=category, listings=listings)


# about/contact us
@routes.route('/about_us',methods=["GET"])
def about_us():
    return render_template("about_us.html")

@routes.route('/contact_us',methods=["GET"])
def contact_us():
    return render_template("contact_us.html")