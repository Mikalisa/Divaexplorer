import os
from tempfile import mkdtemp

# Database Config
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = False



# Mail server Config
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is not None
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = ('From the website','support@divaexplorer-tvj.co.uk')
MAIL_MAX_EMAILS = 5
MAIL_ASCII_ATTACHMENTS = False


# Session Config
SESSION_FILE_DIR = mkdtemp()
SESSION_PERMANENT = False
SESSION_TYPE = "filesystem"


# Whoosh Config
WHOOSH_BASE = 'whoosh'