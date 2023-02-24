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
