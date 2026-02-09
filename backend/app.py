from waitress import serve
from flask import Flask, send_from_directory
from application.config import Config, UPLOAD_FOLDER, COMMENTS_FOLDER
from application.database import db
from application.functions import create_folder
from flask_cors import CORS
from flask_migrate import Migrate, upgrade
from application.resources import api
from application.create_data import (
    create_default_document_status,
    create_order_statuses
)

from sqlalchemy import inspect
import os
import sys
from pathlib import Path


migrate = Migrate()

# --------- IMPORTANT: path handling for PyInstaller ----------


def resource_path(relative_path):
    """Get absolute path to resource (works for dev and PyInstaller)"""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = Path(__file__).resolve().parent

    return os.path.join(base_path, relative_path)


VUE_DIST = resource_path("frontend_dist")


def create_app():
    app = Flask(__name__, static_folder=VUE_DIST, static_url_path="/")
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    app.app_context().push()
    # ---------- Serve Vue ----------

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_vue(path):
        if path != "" and os.path.exists(os.path.join(VUE_DIST, path)):
            return send_from_directory(VUE_DIST, path)
        return send_from_directory(VUE_DIST, "index.html")
    return app, db


app, db = create_app()


with app.app_context():
    inspector = inspect(db.engine)

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        inspector = inspect(db.engine)

        if not inspector.get_table_names():
            print("First run detected — creating database")
            db.create_all()
            create_default_document_status()
            create_order_statuses()
        else:
            print("Running migrations (if any)")
            upgrade()

    db.create_all()
    create_default_document_status()
    create_order_statuses()


if __name__ == "__main__":
    port = 8080
    if getattr(sys, 'frozen', False):
        serve(app, host='127.0.0.1', port=port)
    else:
        app.run(debug=True, port=port)
