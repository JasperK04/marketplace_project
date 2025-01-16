from flask import render_template, redirect,url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, ListingForm, EditProfileForm
from app.models.User import User
from app.models.Category import Category
import sqlalchemy as sa
from sqlalchemy import select
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename


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
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# Profile stuff
@app.route('/profile/<user_id>')
def profile(user_id):
    user = db.get_or_404(User,user_id)
    listings = db.session.execute(
        sa.select(Listing).where(Listing.userID == user.id)).scalars()
    # Will get this sorted out later, hopefully
    #profile_pic = db.session.execute(
    #    sa.select(Image).where(Image.userID == user.id)).scalars()
    return render_template('profile.html', user=user, listings=listings)


@app.route('/profile/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    user = db.get_or_404(User,user_id)
    listings = db.session.execute(
        sa.select(Listing).where(Listing.userID == user.id)).scalars()

    if user.id != current_user.id:
        flash("You are not allowed to edit this profile.")
        return render_template("profile.html", user=user, listings=listings)
    
    form = EditProfileForm()
    if form.validate_on_submit():
        user.about_me = form.about_me.data
        user.name = form.name.data
        db.session.add(user)
        db.session.commit()
        return render_template('profile.html', user=user, listings=listings)

    return render_template('edit_profile.html', user=user, form=form)


# Listings
@app.route("/listings", methods=["GET"])
def listings():
    listings = db.session.query(Listing).all()
    return render_template("listings.html", listings=listings)


@app.route("/listings/<int:listing_id>", methods=["GET"])
def listing(listing_id):
    listing = db.get_or_404(Listing, listing_id).to_dict()
    return render_template("listing.html", listing=listing)

 

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
        new_image = Image(img=file.read(),filename=secure_filename(file.filename),mimetype=file.mimetype,
                          type='listing',listingID=new_listing.id)
        db.session.add(new_image)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_listing.html',title='Add listing',form=form)
