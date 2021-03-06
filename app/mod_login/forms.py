# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form  # , RecaptchaField
# Import Form elements such as TextField and BooleanField (optional)
from wtforms import PasswordField, StringField  # BooleanField
# Import Form validators
from wtforms.validators import DataRequired, Email, EqualTo


# Define the login form (WTForms)

class LoginForm(Form):
    email = StringField('Email Address', [Email(),
                                          DataRequired(message='Forgot your email address?')])
    password = PasswordField('Password', [
        DataRequired(message='Must provide a password. ;-)')])
