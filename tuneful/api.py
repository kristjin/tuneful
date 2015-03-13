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

# JSON Schema describing the structure of a post
file_schema = {
    "properties": {
        "file": {"type": "object"}
    },
    "required": ["file"]
}


@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)


@app.route("/api/songs", methods=["POST"])
@decorators.require("application/json")
@decorators.accept("application/json")
def songs_post():
    """ Add a new song - after file is uploaded """
    # Get JSON from the request
    data = request.json

    # Check that the JSON supplied is valid
    # If not you return a 422 Unprocessable Entity
    try:
        validate(data, file_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422,
                        mimetype="application/json")

    # Extract the file data from the request
    file = data["file"]
    # Verify that this file exists in the database
    db_file = session.query(models.File).get(file["id"])

    # Create the song object, linking the file_id
    song = models.Song(file_id=file["id"])
    # Add the song to the session and commit it
    session.add(song)
    session.commit()

    # Return a 201 Created, containing the post as JSON and with the
    # Location header set to the location of the post
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("songs_get")}
    return Response(data, 201, headers=headers,
                    mimetype="application/json")


@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """Get a list of songs"""
    # Get all the relevant songs
    songs = session.query(models.Song).all()

    # Convert the songs objects to JSON and return a response
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")

