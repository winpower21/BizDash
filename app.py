from flask import Flask
from application.database import db, whooshee
from application.functions import create_folder
from flask_migrate import Migrate
import os


app = None
migrate = Migrate()
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT,'static','files')

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3' 
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)
    migrate.init_app(app, db)
    whooshee.init_app(app)
    app.app_context().push()
    return app, db


app, db = create_app()

from application.controllers import *


with app.app_context():
    db.create_all()
    whooshee.reindex()


if __name__ == '__main__':
    create_folder(UPLOAD_FOLDER)
    app.run(debug=True)