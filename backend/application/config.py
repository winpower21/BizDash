import os


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'frontend', 'UPLOADS')

class Config():
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.sqlite3'
    SECRET_KEY = "secret_key"
    UPLOAD_FOLDER = UPLOAD_FOLDER
    WTF_CSRF_ENABLED = False
