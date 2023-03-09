#!/usr/bin/python3
"""importing model libraries"""
from app import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from flask import current_app, session


@login_manager.user_loader
def load_user(user_id):
    """load user from database ussing user id"""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Create User instance table inside database"""

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)
    birthday = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    gender = db.Column(db.String(10), nullable = False, default = 'Female')
    comments = db.relationship('Comment', backref='author', lazy = True)
 
    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Comment(db.Model):
    """Create new comment instance table and return comment title and date posted"""

    id = db.Column(db.Integer, primary_key = True)
    date_posted = db.Column(db.DateTime,
                            nullable = False,
                            default = datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    content_chatbot = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id'),
                        nullable = False)
    product_id = db.Column(db.Integer,
                           db.ForeignKey('product.id'),
                           nullable = False)

    def __repr__(self):
        return ("Comment('{}','{}')".format(self.title, self.date_posted))

class Product(db.Model):
    __tablename__ = 'product'
    # __searchable__ = ['title','description']
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    title = db.Column(db.String(100), nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    price = db.Column(db.Integer, nullable = False)
    description = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(), nullable = True, default='default.jpg')
    product_size = db.Column(db.String(50))
    product_type = db.Column(db.String(50))
    type_detail = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable = False)
    cartitems = db.relationship('CartItem', backref='Product', lazy = True)
    comments = db.relationship('Comment', backref='product', lazy = True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f"Product('{self.title}','{self.price}','{self.image_file}')"

class Category(db.Model):
    """Create product category instance table and return informaion about category"""

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    products = db.relationship('Product', backref='type', lazy = True)
    def __repr__(self):
        return ("Category('{}')".format(self.name))

class CartItem(db.Model):
    """Creates Cart item instance table and return information about cart items"""

    id = db.Column(db.Integer, primary_key = True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    infor_id = db.Column(db.Integer, db.ForeignKey('infor.id'))
    def __repr__(self):
        return ("CartItem('{}')".format(self.quantity))

class Infor(db.Model):
    """Creates product Information instance table and return information about it"""
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    address = db.Column(db.String(100), nullable = False)
    country = db.Column(db.String(100), nullable = False)
    city = db.Column(db.String(100), nullable = False)
    postcode = db.Column(db.String(100), nullable = False)
    phone = db.Column(db.String(100), nullable = False)
    cartitems = db.relationship("CartItem", backref="cart", lazy = 'dynamic')
    order_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    total_price = db.Column(db.Integer, nullable = False)
    def __repr__(self):
        return ("Infor('{}','{}','{}')".format(self.name, self.address, self.phone))

class User_behavior(db.Model):
    __tablename__ = 'user_behavior'
    """stores information about the user behavior,
    such as the user ID, product ID, behavior type"""

    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    behavior_type = db.Column(db.Text)
    behavior_time = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
