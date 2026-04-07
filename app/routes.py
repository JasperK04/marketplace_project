import math
import os
from urllib.parse import urlencode, urlsplit

import sqlalchemy as sa
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select

from app.config import config
from app.extensions import db
from app.extensions import login as login_manager
from app.forms import EditProfileForm, ListingForm, LoginForm, RegistrationForm
from app.models.Category import Category
from app.models.Image import Image
from app.models.Listing import Listing
from app.models.User import User
from app.route_utils import (
    delete_images,
    get_open_listings_with_images,
    resize_upload_image,
)

app_config = config[os.getenv("FLASK_ENV", "development")]

routes = Blueprint("routes", __name__)


def can_view_restricted_pages():
    return current_user.is_authenticated and current_user.is_admin


def normal_path(path):
    parts = path.strip("/").replace("_", " ").split("/")

    actions = ["edit", "delete"]
    action = parts[-1] if parts[-1] in actions else None
    if action:
        main_route = parts[0]
        if main_route.endswith("s"):
            main_route = main_route[:-1]

        return f"{action} {main_route}"
    else:
        # No action, just return the path in a readable format
        return " ".join(part for part in parts)


def parse_price_filter(value: str | None):
    if not value:
        return None
    try:
        return Listing.normalize_price(value)
    except (ValueError, TypeError):
        return None


def build_filter_params(args, filter_keys):
    params = {}
    for key in filter_keys:
        value = args.get(key)
        if value is None or value == "":
            continue
        params[key] = value
    return params, urlencode(params)


@login_manager.unauthorized_handler
def unauthorized():
    attempted_page = request.path
    page = normal_path(attempted_page)
    flash(f'You must be logged in to access "{page}".', "error")
    return redirect(url_for("routes.login", next=attempted_page))


@routes.route("/", methods=["GET"])
@routes.route("/index", methods=["GET"])
def index():
    # Get query parameters for pagination
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 36, type=int)

    # Fetch listings with pagination
    listings, per_page, total_pages = get_open_listings_with_images(
        page=page, per_page=per_page
    )
    current_page_url = url_for("routes.index")

    categories = db.session.query(Category).all()

    if page > total_pages:
        page = total_pages
    elif page < 1:
        page = 1

    return render_template(
        "index.html",
        listings=listings,
        current_page=page,
        total_pages=total_pages,
        per_page=per_page,
        current_page_url=current_page_url,
        categories=categories,
        filter_params={},
        query_string="",
    )


@routes.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("routes.index"))
    form = LoginForm()
    if form.validate_on_submit():
        next_page = request.args.get("next")
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "error")
            return redirect(url_for("routes.login", next=next_page))
        if user.is_deactivated:
            flash("Account is deactivated", "error")
            return redirect(url_for("routes.login", next=next_page))
        login_user(user, remember=form.remember_me.data)
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
        file = request.files.get("file")
        if db.session.scalar(sa.select(User).where(User.name == form.username.data)):
            flash("Username already taken", "error")
            return redirect(url_for("register"))
        if db.session.scalar(sa.select(User).where(User.email == form.email.data)):
            flash("Email address already exists.", "error")
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
        db.session.flush()

        if file:
            img = resize_upload_image(
                file=file, ratio=(1, 1), size=(200, 200), user_id=user.id
            )
            db.session.add(img)
        db.session.commit()
        flash("Congratulations, you are now a registered user!", "success")
        return redirect(url_for("routes.login"))
    return render_template("register.html", title="Register", form=form)


# Profile stuff
@routes.route("/profile/<user_name>", methods=["GET"])
@login_required
def profile_by_name(user_name: str):
    print(user_name)
    user = db.session.scalar(select(User).where(User.username == user_name))
    if not user:
        return redirect(url_for("index"))
    if user.is_deactivated and not can_view_restricted_pages():
        return redirect(url_for("index"))

    profile_pic = db.session.execute(
        sa.select(Image).where(Image.userID == user.id)
    ).scalar()

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 36, type=int)

    # Fetch listings with pagination
    listings, per_page, total_pages = get_open_listings_with_images(
        by_user=user.id, page=page, per_page=per_page
    )
    current_page_url = url_for("routes.profile", user_id=user.id)

    if page > total_pages:
        page = total_pages
    elif page < 1:
        page = 1

    return render_template(
        "profile.html",
        user=user,
        profile_pic=profile_pic,
        listings=listings,
        current_page=page,
        total_pages=total_pages,
        per_page=per_page,
        current_page_url=current_page_url,
        filter_params={},
        query_string="",
    )


@routes.route("/profile/<int:user_id>", methods=["GET"])
@login_required
def profile(user_id: int):
    user = db.get_or_404(User, user_id)
    return profile_by_name(user.username)


@routes.route("/profile/<user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(user_id):
    user = db.get_or_404(User, user_id)

    # Get query parameters for pagination
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 24, type=int)

    # Fetch listings with pagination
    listings, per_page, total_pages = get_open_listings_with_images(
        page=page, per_page=per_page, by_user=user_id
    )
    current_page_url = url_for("routes.profile", user_id=current_user.id)

    if page > total_pages:
        page = total_pages
    elif page < 1:
        page = 1

    if user.id != current_user.id:
        flash("You are not allowed to edit this profile.warning")
        return render_template(
            "profile.html",
            user=user,
            listings=listings,
            profile_pic="https://placehold.co/200x200",
            current_page=page,
            total_pages=total_pages,
            per_page=per_page,
            current_page_url=current_page_url,
            filter_params={},
            query_string="",
        )

    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        file = request.files.get("file")
        user.about_me = form.about_me.data
        user.username = form.username.data
        db.session.add(user)
        db.session.flush()
        if file:
            delete_images(user_id=user.id)

            image = resize_upload_image(
                file=file, ratio=(1, 1), size=(200, 200), user_id=user_id
            )
            db.session.add(image)
        db.session.commit()

        profile_pic = db.session.execute(
            sa.select(Image).where(Image.userID == current_user.id)
        ).scalar()
        return render_template(
            "profile.html",
            listings=listings,
            current_page=page,
            total_pages=total_pages,
            per_page=per_page,
            current_page_url=current_page_url,
            filter_params={},
            query_string="",
            profile_pic=profile_pic,
            user=user,
        )

    return render_template("edit_profile.html", user=user, form=form)


# Listings
@routes.route("/listings", methods=["GET"])
def listings():
    # Get query parameters for pagination
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 36, type=int)
    search_query = request.args.get("q", "", type=str).strip()
    min_price_raw = request.args.get("min_price", "", type=str).strip()
    max_price_raw = request.args.get("max_price", "", type=str).strip()
    selected_condition = request.args.get("condition", "", type=str).strip()
    selected_category = request.args.get("category", type=int)

    min_price = parse_price_filter(min_price_raw)
    max_price = parse_price_filter(max_price_raw)

    condition_enum = None
    if selected_condition:
        try:
            condition_enum = Listing.normalize_condition(selected_condition)
            selected_condition = condition_enum.value
        except ValueError:
            selected_condition = ""

    # Fetch listings with pagination
    listings, per_page, total_pages = get_open_listings_with_images(
        page=page,
        per_page=per_page,
        search=search_query,
        min_price=min_price,
        max_price=max_price,
        condition=condition_enum,
        by_category=selected_category,
    )
    current_page_url = url_for("routes.listings")

    categories = db.session.query(Category).all()
    filter_params, query_string = build_filter_params(
        request.args,
        ["q", "category", "condition", "min_price", "max_price"],
    )

    if page > total_pages:
        page = total_pages
    elif page < 1:
        page = 1

    max_price_query = sa.select(sa.func.max(Listing.price)).where(
        Listing.sold.is_(False), Listing.is_deactivated.is_(False)
    )
    if search_query:
        term = f"%{search_query}%"
        max_price_query = max_price_query.where(
            sa.or_(Listing.title.ilike(term), Listing.description.ilike(term))
        )
    max_price_cents = db.session.scalar(max_price_query) or 0
    max_price_limit = int(math.ceil(max_price_cents / 100))

    return render_template(
        "listings.html",
        listings=listings,
        current_page=page,
        total_pages=total_pages,
        per_page=per_page,
        current_page_url=current_page_url,
        categories=categories,
        search_query=search_query,
        min_price=min_price_raw,
        max_price=max_price_raw,
        selected_condition=selected_condition,
        selected_category=selected_category,
        condition_labels=Listing.CONDITION_LABELS,
        filter_params=filter_params,
        query_string=query_string,
        max_price_limit=max_price_limit,
    )


@routes.route("/listings/<int:listing_id>", methods=["GET"])
def listing(listing_id: int):
    listing = db.get_or_404(Listing, listing_id).to_dict()
    image = db.session.execute(
        sa.select(Image).where((Image.listingID == listing_id))
    ).scalar()
    if image:
        listing["filename"] = image.filename
    if listing["is_deactivated"] and not can_view_restricted_pages():
        return redirect(url_for("routes.listings"))
    return render_template(
        "listing.html",
        listing=listing,
        condition_labels=Listing.CONDITION_LABELS,
    )


@routes.route("/add_listing", methods=["GET", "POST"])
@login_required
def add_listing():
    form = ListingForm()
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
                "condition": Listing.normalize_condition(form.condition.data),
                "userID": current_user.id,
            },
            sold=False,
        )
        db.session.add(new_listing)
        db.session.flush()
        if file:
            image = resize_upload_image(
                file=file, ratio=(3, 2), size=(600, 400), listing_id=new_listing.id
            )
            db.session.add(image)
        db.session.commit()
        return redirect(url_for("routes.index"))
    return render_template("add_listing.html", title="Add listing", form=form)


@routes.route("/listings/<int:listing_id>/edit", methods=["GET", "POST"])
@login_required
def edit_listing(listing_id: int):
    listing = db.get_or_404(Listing, listing_id)

    if listing.userID != current_user.id:
        flash("You are not allowed to edit this listing.", "warning")
        return redirect(
            url_for("routes.index")
        )  # this depends on where the edit button/link will be placed

    form = ListingForm(obj=listing)

    if not form.validate_on_submit():
        form.category.data = db.session.scalar(
            select(Category.name).where(Category.id == listing.categoryID)
        )

        if listing.price is not None:
            form.price.data = f"{listing.price / 100:.2f}".replace(".", ",")

    form.submit.label.text = "Edit listing"

    if form.validate_on_submit():
        file = request.files.get("file")
        if file:
            # delete old images on disk and in the database
            delete_images(listing_id=listing_id)

            image = resize_upload_image(
                file=file, ratio=(3, 2), size=(600, 400), listing_id=listing_id
            )

            db.session.add(image)
            db.session.commit()
        listing.title = Listing.normalize_title(form.title.data)
        listing.categoryID = db.session.scalar(
            select(Category.id).where(Category.name == form.category.data)
        )
        listing.description = Listing.normalize_description(form.description.data)
        listing.price = Listing.normalize_price(form.price.data)
        listing.condition = Listing.normalize_condition(form.condition.data)
        db.session.add(listing)
        db.session.commit()
        return redirect(
            url_for("routes.profile", user_id=current_user.id)
        )  # this depends on where the edit button/link will be placed
    return render_template("add_listing.html", title="Edit listing", form=form)


@routes.route("/listings/<int:listing_id>/delete", methods=["GET", "POST"])
@login_required
def delete_listing(listing_id: int):
    listing = db.get_or_404(Listing, listing_id)

    if listing.userID != current_user.id:
        flash("You are not allowed to delete this listing.", "warning")
        return redirect(
            url_for("routes.index")
        )  # this depends on where the edit button/link will be placed

    delete_images(listing_id, "listing")

    db.session.delete(listing)
    db.session.commit()
    return redirect(
        url_for("routes.profile", user_id=current_user.id)
    )  # this depends on where the edit button/link will be placed


# Categories
@routes.route("/categories", methods=["GET"])
def categories():
    db_categories = db.session.query(Category).all()

    listings_per_cat = {
        category.id: {"category": category, "listings": []}
        for category in db_categories
    }

    # Preload all recent listings for all categories
    all_recent_listings = db.session.query(Listing).order_by(Listing.id.desc()).all()

    # Get all images for these listings in one query
    listing_ids = [listing.id for listing in all_recent_listings]
    images = db.session.query(Image).filter(Image.listingID.in_(listing_ids)).all()
    image_map = {img.listingID: img.filename for img in images}

    # Assign listings to categories and attach image filename
    for listing in all_recent_listings:
        cat_id = listing.categoryID
        if (
            cat_id in listings_per_cat
            and len(listings_per_cat[cat_id]["listings"]) < 12
        ):
            listing_dict = listing.to_dict()
            if listing.id in image_map:
                listing_dict["filename"] = image_map[listing.id]
            listings_per_cat[cat_id]["listings"].append(listing_dict)

    categories = db.session.query(Category).all()

    return render_template(
        "categories.html", listings_per_cat=listings_per_cat, categories=categories
    )


@routes.route("/categories/<int:category_id>", methods=["GET"])
def category(category_id: int):
    category = db.get_or_404(Category, category_id)  # pylint: disable=redefined-outer-name
    print(category_id)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 24, type=int)
    search_query = request.args.get("q", "", type=str).strip()
    min_price_raw = request.args.get("min_price", "", type=str).strip()
    max_price_raw = request.args.get("max_price", "", type=str).strip()
    selected_condition = request.args.get("condition", "", type=str).strip()

    min_price = parse_price_filter(min_price_raw)
    max_price = parse_price_filter(max_price_raw)

    condition_enum = None
    if selected_condition:
        try:
            condition_enum = Listing.normalize_condition(selected_condition)
            selected_condition = condition_enum.value
        except ValueError:
            selected_condition = ""

    listings, per_page, total_pages = get_open_listings_with_images(
        by_category=category_id,
        page=page,
        per_page=per_page,
        search=search_query,
        min_price=min_price,
        max_price=max_price,
        condition=condition_enum,
    )
    current_page_url = url_for("routes.category", category_id=category_id)

    filter_params, query_string = build_filter_params(
        request.args,
        ["q", "condition", "min_price", "max_price"],
    )

    if page > total_pages:
        page = total_pages
    elif page < 1:
        page = 1

    max_price_query = sa.select(sa.func.max(Listing.price)).where(
        Listing.sold.is_(False),
        Listing.is_deactivated.is_(False),
        Listing.categoryID == category_id,
    )
    if search_query:
        term = f"%{search_query}%"
        max_price_query = max_price_query.where(
            sa.or_(Listing.title.ilike(term), Listing.description.ilike(term))
        )
    max_price_cents = db.session.scalar(max_price_query) or 0
    max_price_limit = int(math.ceil(max_price_cents / 100))

    return render_template(
        "category.html",
        category=category,
        listings=listings,
        current_page=page,
        total_pages=total_pages,
        per_page=per_page,
        current_page_url=current_page_url,
        search_query=search_query,
        min_price=min_price_raw,
        max_price=max_price_raw,
        selected_condition=selected_condition,
        condition_labels=Listing.CONDITION_LABELS,
        filter_params=filter_params,
        query_string=query_string,
        max_price_limit=max_price_limit,
    )


@routes.route("/categories/<category_name>", methods=["GET"])
def category_name(category_name: str):  # pylint: disable=redefined-outer-name
    cat = db.session.scalar(
        select(Category).where(Category.name == category_name.title())
    )  # pylint: disable=redefined-outer-name
    if cat is None:
        return redirect(url_for("routes.index"))
    return category(cat.id)


# about/contact us
@routes.route("/about_us", methods=["GET"])
def about_us():
    return render_template("about_us.html")


@routes.route("/contact_us", methods=["GET"])
def contact_us():
    return render_template("contact_us.html")
