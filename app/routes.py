from flask import render_template, redirect,url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm,RegistrationForm, ListingForm
from app.models.User import User
from app.models.Category import Category
import sqlalchemy as sa
from sqlalchemy import select, and_
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename
import os
from PIL import Image as IM


from . import app, db
from .models.Listing import Listing
from .models.Category import Category
from .models.Image import Image

@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    listings = db.session.query(Listing).filter_by(sold=False).all()
    return render_template("index.html", listings=listings)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.name == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        #flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/profile/<user_id>')
def profile(user_id):
    user = db.get_or_404(User,user_id)
    listings = db.session.execute(
        sa.select(Listing).where(Listing.userID == user.id)).scalars()
    profile_pic = db.session.execute(
        sa.select(Image).where(Image.userID == user.id)).scalars()
    return render_template('profile.html', user=user, listings=listings, profile_pic=profile_pic)


# Listings
@app.route("/listings", methods=["GET"])
def listings():
    all_listings = db.session.query(Listing).all()
    listings = []
    for listing in all_listings:
        image = db.session.execute(sa.select(Image).where(and_(Image.listingID==listing.id, Image.variant == 'original'))).scalar()
        listings.append({
            "id": listing.id,
            "title": listing.title,
            "price": listing.price,
            "filename": image.filename if image else None
        })
    return render_template("listings.html", listings=listings)


@app.route("/listings/<int:listing_id>", methods=["GET"])
def listing(listing_id):
    listing = db.get_or_404(Listing, listing_id).to_dict()
    image = db.session.execute(sa.select(Image).where(and_(Image.listingID==listing_id, Image.variant == 'resized'))).scalar()
    return render_template("listing.html", listing=listing, image=image)

 

@app.route('/add_listing',methods=['GET','POST'])
@login_required
def add_listing():
    form = ListingForm()
    form.category.choices = [category.name for category in db.session.query(Category).all()]
    if form.validate_on_submit():
        file = request.files.get('file')
        cat_id = db.session.scalar(select(Category.id).where(Category.name == form.category.data))
        new_listing = Listing(title=form.title.data,categoryID=cat_id,description=form.description.data,
                              price=form.price.data,userID=current_user.id)
        db.session.add(new_listing)
        db.session.flush()
        new_images = resize_upload_image(file,new_listing)
        db.session.add(new_images[0])
        db.session.add(new_images[1])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_listing.html',title='Add listing',form=form)


def resize_upload_image(file, listing):
    image = IM.open(file)
    target_sizes = [(300, 200), (600, 400)]
    folder_names = ['UPLOAD_FOLDER', 'RESIZED_FOLDER']
    file_prefixes = ['', 'resized_']
    variants = ['original','resized']
    images = []

    for size, folder, prefix, variant in zip(target_sizes, folder_names, file_prefixes, variants):
        img = image.copy()
        # if image is smaller than preferred size, thumbnail (resize with same aspect ratio) cannot be used 
        if img.width < size[0] or img.height < size[1]:
            img = img.resize(size,resample=1) # 1=LANCZOS resampling leads to higher quality pictures
        else:
            img.thumbnail(size,resample=1) 

        filename = prefix + secure_filename(file.filename)
        filepath = os.path.join(app.config[folder], filename)
        os.makedirs(app.config[folder], exist_ok=True)
        img.save(filepath)

        new_image = Image(
            filename=filename,
            filepath=filepath,
            type='listing',
            listingID=listing.id,
            variant=variant
        )
        images.append(new_image)

    return images