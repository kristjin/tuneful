import os.path

from tuneful import app

def upload_path(filename=""):
    return os.path.join(app.root_path, app.config["UPLOAD_FOLDER"], filename)
