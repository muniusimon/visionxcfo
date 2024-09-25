import os
import secrets
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request
from visionxcfo import app, db, bcrypt
from visionxcfo.forms import RegistrationForm, LoginForm, UpdateAccountForm
from visionxcfo.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

posts = [
    {
        'author': 'Simon Kinuthia',
        'title': "My first post",
        'content': 'First Post content',
        'dateposted': 'April 3, 2023'

    },
    {
        'author': 'Kinuthia',
        'title': "My second post",
        'content': 'I am who I am',
        'dateposted': 'April 3, 2024'

    }

    ]

@app.route("/", methods=['GET', 'POST'])
def home():
    creative_prompt = None
    if request.method == 'POST':
        # Retrieve the input from the user
        keywords = request.form.get('keywords')
        themes = request.form.get('themes')
        concepts = request.form.get('concepts')
    

        # Create a prompt for the AI model
        ai_prompt = (
            f"Generate a creative idea based on the following inputs:\n"
            f"Keywords: {keywords}\n"
            f"Themes: {themes}\n"
            f"Concepts: {concepts}\n"
            f"Creative Idea:"
        )

        try:
            response = openai.Completion.create(
                engine="text-davinci-003",  # Use the desired model
                prompt=ai_prompt,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.7,
            )
            creative_prompt = response.choices[0].text.strip()
        except Exception as e:
            creative_prompt = f"An error occurred: {e}"

    return render_template('home.html', creative_prompt=creative_prompt)






@app.route("/about")
def about ():
    return render_template("about.html", title = 'About')

@app.route("/contact")
def contact ():
    return render_template("contact.html")

@app.route("/register", methods = ['GET', 'POST'])
def register ():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account Created for {form.username.data}!', 'success')
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User (username= form.username.data, email = form.email.data, password = hashed_password )
        db.session.add(user)
        db.session.commit()
        flash ('You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)

@app.route("/login", methods=['GET', 'POST'])
def login ():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get ('next')
            return redirect(next_page) if next_page else redirect (url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email or password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout ():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext (form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profle_pics', picture_fn)
    form_picture.save (picture_path)

    return picture_fn 



@app.route('/account', methods=['GET', 'POST'])
@login_required
def account ():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Your account has been update to {form.username.data}', 'success')
        return redirect (url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = "images/" + current_user.image_file)
    return render_template('account.html', title = "account", image_file = image_file, form = form) 

