#!/usr/bin/python3
"""importing model libraries"""
from models import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from flask import current_app, session


@login_manager.user_loader
def load_user(user_id):
    """load user from database ussing user id"""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Create User class inside database"""
    id = db.Column(db.Integer, priery_key=True)
    user_name = db.Column(db.string(20), unique=True, nullable=False)
    email = db.Column(db.string(120), unique=True, nulable=False)
    password = db.Column(db.String(60), nullable = False)
    birthday = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    gender = db.Column(db.String(10), nullable = False, default = 'Female')
    comments = db.relationship('Comment', backref='author', lazy = True)
    def __repr__(self):
        return ("User('{}','{}')".format(self.username, self.email))

class Comment(db.Model):
    """Create new comment instance and return comment title and date posted"""
    id = db.Column(db.Integer, primary_key = True)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    content_chatbot = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)
    def __repr__(self):
        return ("Comment('{}','{}')".format(self.title, self.date_posted))
