from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask import request


import os



db = SQLAlchemy()

mail = Mail()

login_manager = LoginManager()


GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


PAYPAL_ACCOUNT = os.environ.get('PAYPAL_ACCOUNT')

PAYMENT_SUCCESS = os.environ.get('PAYMENT_SUCCESS')

IPN_LINK = os.environ.get('IPN_LINK')

HOME_PAGE = os.environ.get('HOME_PAGE')


POSTS_PER_PAGE = 3

