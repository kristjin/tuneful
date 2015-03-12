import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

import models
import decorators
from tuneful import app
from database import session
from utils import upload_path


@app.route("/api/songs")
@decorators.accept("application/json")
def songs_get():
    """Get a list of songs"""
    # Get all the relevant songs
    songs = session.query(models.Song).all()

    # Convert the songs objects to JSON and return a response
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")
