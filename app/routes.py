from flask import render_template, redirect,url_for, request, flash
from flask_login import current_user, login_user, logout_user
from app.forms import LoginForm,RegistrationForm
from app.models.User import User
import sqlalchemy as sa
from urllib.parse import urlsplit


from . import app, db
from .models.Listing import Listing


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
            sa.select(User).where(User.username == form.username.data))
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
