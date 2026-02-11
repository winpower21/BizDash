import platform
from pathlib import Path
import os
from .functions import create_folder

def get_app_data_dir():
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / "BizDash"
    else:
        return Path.home() / ".bizdash"

APP_FOLDER = get_app_data_dir()
UPLOAD_FOLDER = os.path.join(APP_FOLDER, "uploads")
COMMENTS_FOLDER = os.path.join(UPLOAD_FOLDER, "comments")
DB_PATH = os.path.join(APP_FOLDER, "bizdash.sqlite3")
create_folder(UPLOAD_FOLDER)
create_folder(COMMENTS_FOLDER)
LOG_FILE = os.path.join(APP_FOLDER, "backend.log")


class Config():
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    UPLOAD_FOLDER = UPLOAD_FOLDER
    COMMENTS_FOLDER = COMMENTS_FOLDER
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
