from flask import Flask
from application.config import Config, UPLOAD_FOLDER
from application.database import db, whooshee
from application.functions import create_folder
from flask_cors import CORS
from flask_migrate import Migrate
from application.resources import api
import os



migrate = Migrate()



def create_app():
    app = Flask(__name__, template_folder='frontend', static_folder='frontend')
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    whooshee.init_app(app)
    api.init_app(app)
    app.app_context().push()
    return app, db


app, db = create_app()

from application.controllers import *


with app.app_context():
    db.create_all()
    whooshee.reindex()


if __name__ == '__main__':
    create_folder(UPLOAD_FOLDER)
    app.run(debug=True, port=8000)
