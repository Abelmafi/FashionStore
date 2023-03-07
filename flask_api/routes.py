#!/usr/bin/python3
"""RESTApi using flask application"""
from flask import redirect, flash, render_template, url_for, request
from fashionshop.forms import RegistrationForm,LoginForm, InforForm, UserForm
from fashionshop import db, bcrypt, app, es
from fashionshop.models import *
from flask_login import current_user, login_user, login_required, logout_user
from product_recommender import *
from chatbot import bot


@app.route("/", methods=['GET', 'POST','PUT'])
@app.route("/home")
def home():
    """Api that redirect to home page"""
    session.permanent = True

    return render_template('home.html')

@app.route("/about")
def about():
    """Api that redirect to about page"""

    return render_template('about.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Api that redirect to registration page"""

    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data,
                    email = form.email.data,
                    password = password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account have been created!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form = form, title = 'Register')

@app.route("/login", methods=['GET','POST'])
def login():
    """Api that redirect to user login page"""

    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            flash(f'Login succesfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash(f'Please check the information!','danger')
    return render_template('login.html', form = form, title = 'Login')

@app.route('/ssearch')
def ssearch():
    query = request.args.get('q', '')
    if query:
        products = search_products(query)
    else:
        products = []
    print (f"here are the products", products)
    return render_template('search.html', query=query, products=products)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Api that redirect to contact admin page"""

    session['firstname'] = request.form.get('firstname')
    session['lastname'] = request.form.get('lastname')
    session['email'] = request.form.get('email')
    session['subject'] = request.form.get('subject')
    session['message'] = request.form.get('message')
    print(session['firstname'], session['lastname'], session['email'],
          session['subject'],session['message'])
    if session['firstname'] != None:
        flash(f'Message sent!', 'success')
    return render_template('contact.html', tilte = 'Contact')

@app.route('/categories')
def categories():
    """Api that redirect to product caegories page"""

    page = request.args.get('page', 1, type = int)
    products = Product.query.order_by(Product.title.desc()).paginate(page = page, per_page = 12)
    categories = Category.query.all()
    total_results = Product.query.count()
    return render_template('categories.html',
                            title = 'Categories',
                            products = products,
                            categories = categories,
                            totals = total_results)

