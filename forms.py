from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from fashionshop.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    """Create Registration flask form"""
    username = StringField('Username', validators=[DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

