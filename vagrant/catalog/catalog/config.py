import os

DATABASE_URI = 'sqlite:///catalog/catalog.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'a secret'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
