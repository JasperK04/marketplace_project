from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from sqlalchemy import outerjoin, select
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename
import os
import uuid
from PIL import Image as IM


from . import app, db
from app.forms import LoginForm, RegistrationForm, ListingForm, EditProfileForm
from .models.User import User
from .models.Listing import Listing
from .models.Category import Category
from .models.Image import Image

def can_view_restricted_pages():
    return current_user.is_authenticated and current_user.is_admin

@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    listings = Listing.find_open_listings()
    return render_template("index.html", listings=listings)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.name == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        if user.is_deactivated:
            flash('Account is deactivated')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


# Profile stuff
@app.route("/profile/<int:user_id>")
def profile(user_id:int):
    user = db.get_or_404(User, user_id)
    if user.is_deactivated and not can_view_restricted_pages():
        return redirect(url_for('index'))
    listings = []
    listings_with_images = (
        db.session.query(Listing, Image.filename)
        .join(Image, (Image.listingID == Listing.id) & (Image.variant == 'original'), isouter=True)
        .filter(Listing.userID == user.id)
        .all()
    )
    for listing, filename in listings_with_images:
        if not listing.is_deactivated:
            if filename:
                listing = listing.to_dict()
                listing["filename"] = filename
                listings.append(listing)
            else:
                listings.append(listing.to_dict())

    # Will get this sorted out later, hopefully
    # profile_pic = db.session.execute(
    #    sa.select(Image).where(Image.userID == user.id)).scalars()
    return render_template("profile.html", user=user, listings=listings)


@app.route("/profile/<user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(user_id):
    user = db.get_or_404(User, user_id)
    listings = db.session.execute(  # pylint: disable=redefined-outer-name
        sa.select(Listing).where(Listing.userID == user.id)
    ).scalars().all()

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
@app.route("/listings", methods=["GET"])
def listings():
    listings = []
    listings_with_images = db.session.query(Listing, Image.filename).join(Image, (Image.listingID == Listing.id) & (Image.variant == 'original'), isouter=True).all()
    for listing, filename in listings_with_images:
        if not listing.sold and not listing.is_deactivated:  # instead of the Listing.find_open_listings()
            if filename:
                listing = listing.to_dict()
                listing["filename"] = filename
                listings.append(listing)
            else:
                listings.append(listing.to_dict())

    # Find all unsold, active listings
    #listings = Listing.find_open_listings()
    #listings = db.session.query(Listing).all()

    return render_template("listings.html", listings=listings)


@app.route("/listings/<int:listing_id>", methods=["GET"])
def listing(listing_id: int):
    listing = db.get_or_404(Listing, listing_id).to_dict()
    image = db.session.execute(sa.select(Image).where((Image.listingID==listing_id) & (Image.variant == 'resized'))).scalar()
    if image:
        listing["filename"] = image.filename
    if listing["is_deactivated"] and not can_view_restricted_pages():
        return redirect(url_for('listings'))
    return render_template("listing.html", listing=listing)


@app.route("/add_listing", methods=["GET", "POST"])
@login_required
def add_listing():
    form = ListingForm()
    form.category.choices = [
        category.name for category in db.session.query(Category).all()
    ]
    form.submit.label.text = 'Add listing'
    if form.validate_on_submit():
        file = request.files.get("file")
        cat_id = db.session.scalar(
            select(Category.id).where(Category.name == form.category.data)
        )
        new_listing = Listing(
            title=Listing.normalize_title(form.title.data),
            categoryID=cat_id,
            description=Listing.normalize_description(form.description.data),
            price=Listing.normalize_price(form.price.data),
            userID=current_user.id,
            sold=False
        )
        db.session.add(new_listing)
        db.session.flush()

        img_org = resize_upload_image(file,(300,200),current_user.id,new_listing.id,'UPLOAD_FOLDER','listing','original')
        img_resized = resize_upload_image(file,(600,400),current_user.id,new_listing.id,'RESIZED_FOLDER','listing','resized')
        db.session.add(img_org)
        db.session.add(img_resized)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_listing.html',title='Add listing',form=form)

@app.route('/edit/<int:listing_id>', methods=['GET','POST'])
@login_required
def edit_listing(listing_id):
    listing = db.get_or_404(Listing,listing_id)

    if listing.userID != current_user.id:
        flash("You are not allowed to edit this listing.")
        return redirect(url_for('index')) # this depends on where the edit button/link will be placed

    form = ListingForm(obj=listing)  # so that form is prefilled (only category is not)
    form.category.choices = [category.name for category in db.session.query(Category).all()]
    form.submit.label.text = 'Edit listing'
    if form.validate_on_submit():
        file = request.files['file']
        if file:
            # delete old images on disk and in the database
            delete_images(listing_id)

            # add new ones
            img_org = resize_upload_image(file,(300,200),current_user.id,listing_id,'UPLOAD_FOLDER','listing','original')
            img_resized = resize_upload_image(file,(600,400),current_user.id,listing_id,'RESIZED_FOLDER','listing','resized')

            db.session.add(img_org)
            db.session.add(img_resized)
            db.session.commit()
        listing.title = Listing.normalize_title(form.title.data)
        listing.categoryID = db.session.scalar(select(Category.id).where(Category.name == form.category.data))
        listing.description = Listing.normalize_description(form.description.data)
        listing.price = Listing.normalize_price(form.price.data)
        db.session.add(listing)
        db.session.commit()
        return redirect(url_for('profile',user_id=current_user.id)) # this depends on where the edit button/link will be placed
    return render_template('add_listing.html',title='Edit listing',form=form)

@app.route('/delete_listing/<int:listing_id>',methods=['GET','POST'])
@login_required
def delete_listing(listing_id):
    listing = db.get_or_404(Listing,listing_id)

    if listing.userID != current_user.id:
        flash("You are not allowed to delete this listing.")
        return redirect(url_for('index')) # this depends on where the edit button/link will be placed

    delete_images(listing_id)

    db.session.delete(listing)
    db.session.commit()
    return redirect(url_for('profile',user_id=current_user.id)) # this depends on where the edit button/link will be placed

def resize_upload_image(file,size,user_id,listing_id,folder,type,variant):
    image = IM.open(file)
    img = image.copy()

    # if image is smaller than preferred size, thumbnail (resize with same aspect ratio) cannot be used
    if img.width < size[0] or img.height < size[1]:
        img = img.resize(size,resample=1) # 1=LANCZOS resampling leads to higher quality pictures
    else:
        img.thumbnail(size,resample=1)
    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    filepath = os.path.join(app.config[folder], filename)
    os.makedirs(app.config[folder], exist_ok=True)
    img.save(filepath)
    if type == "listing":
        new_image = Image(
            filename=filename,
            filepath=filepath,
            type=type,
            listingID=listing_id,
            variant=variant
        )
    else:
        new_image = Image(
            filename=filename,
            filepath=filepath,
            type=type,
            userID=user_id,
            variant=variant
        )

    return new_image

def delete_images(listing_id):
    # first query the filepaths so the files on disk can be deleted
    images = db.session.execute(sa.select(Image).where(Image.listingID == listing_id)).scalars()
    for image in images:
        if image is not None and os.path.exists(image.filepath):
            os.remove(image.filepath)
            # then delete images in database
            db.session.delete(image)
            db.session.commit()


# Categories
@app.route("/categories", methods=["GET"])
def categories():
    db_categories = db.session.query(Category).all()
    categories = {category.id: {"category": category, "listings": []} for category in db_categories}
    # get 10 most recent listings for each category, in a single query
    for category_id, value in categories.items():
        value["listings"] = [listing.to_dict() for listing in db.session.query(Listing).filter_by(categoryID=category_id).order_by(Listing.id.desc()).limit(12).all()]
    return render_template("categories.html", categories=categories)

@app.route("/categories/<int:category_id>", methods=["GET"])
def category(category_id: int):
    category = db.get_or_404(
        Category, category_id
    )  # pylint: disable=redefined-outer-name
    listings = db.session.execute(  # pylint: disable=redefined-outer-name
        sa.select(Listing).where(Listing.categoryID == category.id)
    ).scalars()
    return render_template("category.html", category=category, listings=listings)


@app.route("/categories/<category_name>", methods=["GET"])
def category_name(category_name: str):  # pylint: disable=redefined-outer-name
    category = db.session.scalar(
        select(Category).where(Category.name == category_name.title())
    )  # pylint: disable=redefined-outer-name
    if category is None:
        return redirect(url_for("index"))
    listings = db.session.execute(  # pylint: disable=redefined-outer-name
        sa.select(Listing).where(Listing.categoryID == category.id)
    ).scalars()
    return render_template("category.html", category=category, listings=listings)

