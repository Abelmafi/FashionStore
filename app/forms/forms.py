from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from app.models.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    """Create Registration flask form"""
    username = StringField('Username', validators=[DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
        # length(min=8, message='Password must be at least 8 characters long'),
        # Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])',
        #    message='Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character')])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """validate user name wether the user name exists or not"""
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('This user is existed. Please change username !')

    def validate_email(self, email):
        """validate email adress"""
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('Hey! This email is taken. Please change the email!')

 #   def validate_password(self, password):
 #       """Ensure that the password contains at least one uppercase letter,
 #       one lowercase letter, one digit, and one special character."""
 #       upper = False
 #       lower = False
 #       digit = False
 #       special = False

 #       for char in password.data:
 #           if char.isupper():
 #               upper = True
 #           elif char.islower():
 #               lower = True
 #           elif char.isdigit():
 #               digit = True
 #           else:
 #               special = True

 #       if not (upper and lower and digit and special):
 #           raise ValidationError('Password must contain at least one uppercase letter,
 #                                  one lowercase letter, one digit,
 #                                  and one special character.')


class LoginForm(FlaskForm):
    """setting up login form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class InforForm(FlaskForm):
    """setting up info form"""
    name = StringField('Name', validators = [DataRequired()])
    address = StringField('Address', validators = [DataRequired()])
    # country = StringField('Country', validators = [DataRequired()])
    city = StringField('City', validators = [DataRequired()])
    postcode = StringField('Postcode', validators = [DataRequired()])
    phone = StringField('Phone', validators = [DataRequired()])


class UserForm(FlaskForm):
    """setting up user form"""

    username = StringField('Username', validators=[DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    gender = StringField('Gender', validators=[DataRequired(), Length(min = 4, max = 10)])
    birthday =  DateField('Birthday', format='%b %d %Y', validators=(Optional(),))
    submit = SubmitField('Update')

    def validate_username(self, username):
        """validate user name"""
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('This user is existed. Please change username !')

    def validate_email(self, email):
        """validate email"""
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('Hey! This email is taken. Please change the email!')
