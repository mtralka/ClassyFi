from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from .model import User
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm, SignUp
from . import integration

WTF_CSRF_SECRET_KEY = 'a random string'

auth = Blueprint('auth', __name__)



@auth.route('/login', methods=['GET','POST'])
def login():

	form = LoginForm()

	if form.validate_on_submit():

		email = request.form.get('email')
		password = request.form.get('password')
		remember = True if request.form.get('remember') else False

		if form.validate() == False:
			flash('All fields are required.')
			return render_template('login.html', form = form)

		user = User.query.filter_by(email=email).first()

		if not user or not check_password_hash(user.password, password):
			flash('Please check your login details and try again.')
			return render_template('login.html', form = form)

		login_user(user, remember=remember)

		return redirect(url_for('main.landing'))

	return render_template('login.html', form=form)


@auth.route('/signup', methods=['GET','POST'])
def signup():

	form = SignUp()

	if form.validate_on_submit():

		email = request.form.get('email')
		name = request.form.get('name')
		password = request.form.get('password')

		if form.validate() == False:
			flash('All fields are required.')
			return render_template('signup.html', form = form)

		user = User.query.filter_by(email=email).first()

		if user:
			flash('Email address already exists')
			return render_template('signup.html', form = form)

		new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

		db.session.add(new_user)
		db.session.commit()

		return redirect(url_for('auth.login'))

	return render_template('signup.html', form=form)

@auth.route('/logout')
def logout():
	integration.deletePickle()
	logout_user()
	return redirect(url_for('main.index'))