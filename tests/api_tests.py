import unittest
import os
import shutil
import json
from urlparse import urlparse
from StringIO import StringIO

import sys
print sys.modules.keys()
# Configure our app to use the testing database
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session



class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def test_file_upload(self):
        # Construct form data as a dictionary,
        # Use Py StringIO Class to simulate a file object
        data = {
            "file": (StringIO("File contents"), "test.txt")
        }

        # Send dict to /api/files with content type of multipart/form-data
        response = self.client.post("/api/files",
            data=data,
            content_type="multipart/form-data",
            headers=[("Accept", "application/json")]
        )

        # Response status 201 CREATED expected
        self.assertEqual(response.status_code, 201)
        # Response in JSON?
        self.assertEqual(response.mimetype, "application/json")
        # Decode JSON
        data = json.loads(response.data)
        # Validate file path
        self.assertEqual(urlparse(data["path"]).path, "/uploads/test.txt")
        # Create path from utils.py method
        path = upload_path("test.txt")
        # Verify file is in expected location
        self.assertTrue(os.path.isfile(path))
        # Read the file contents
        with open(path) as f:
            contents = f.read()
        # Verify contents are as expected
        self.assertEqual(contents, "File contents")

    def test_get_uploaded_file(self):
        # create the upload path with the filename
        # upload_path() is defined in utils.py
        path = upload_path("test.txt")
        # Fill the file with some foo
        with open(path, "w") as f:
            f.write("File contents")

        # Obtain the response from the app
        response = self.client.get("/uploads/test.txt")

        # Was the request successful?  200 OK expected.
        self.assertEqual(response.status_code, 200)
        # Is the response in plain text?
        self.assertEqual(response.mimetype, "text/plain")
        # Is the response data the contents of the file uploaded?
        self.assertEqual(response.data, "File contents")

    def testMissingData(self):
        """ Posting a song with missing data """

        # Compile posted data into a dictionary for easy conversion to JSON
        data = {}

        response = self.client.post("/api/songs",
                                    data=json.dumps(data),
                                    content_type="application/json",
                                    headers=[("Accept", "application/json")],
                                    )

        self.assertEqual(response.status_code, 422)

        data = json.loads(response.data)
        self.assertEqual(data["message"], "'file' is a required property")

    def testUnsupportedMimetype(self):
        """ Test Sending Unsupported Mime Type """
        # Compile data in incorrect mimetype
        data = "<xml></xml>"
        # Obtain response from app when posting with unacceptable mimetype
        response = self.client.post("/api/songs",
                                    data=json.dumps(data),
                                    content_type="application/xml",
                                    headers=[("Accept", "application/json")],
                                    )
        # Confirm that response status code is 415 Unsupported Media Type
        self.assertEqual(response.status_code, 415)
        # Confirm that response from app is in JSON
        self.assertEqual(response.mimetype, "application/json")
        # Decode the JSON data
        data = json.loads(response.data)
        # Confirm message is appropriate
        self.assertEqual(data["message"],
                         "Request must contain application/json data")

    def testPostNewSong(self):
        """Post a new song to the DB"""
        # Create a file in the DB for the app to find
        file = models.File(name="BornThisWay.mp3")
        session.add(file)
        session.commit()

        # Compile posted data into a dictionary for easy conversion to JSON
        data = {
            "file": {
                "id": 1
            }
        }

        # Collect the response from the endpoint
        # use json.dumps to convert dict > JSON
        # use content_type to indicate the type of content in data
        response = self.client.post("/api/songs",
                                    data=json.dumps(data),
                                    content_type="application/json",
                                    headers=[("Accept", "application/json")],
                                    )

        # Verify request to endpoint was successful using 201 created
        self.assertEqual(response.status_code, 201)
        # Verify that the response is JSON type
        self.assertEqual(response.mimetype, "application/json")
        # Verify the endpoint is setting the correct Location header
        # This should be the link to the new post
        self.assertEqual(urlparse(response.headers.get("Location")).path,
                         "/api/songs")
        # Decode the response with json.loads
        song = json.loads(response.data)
        # Extrapolate the file info
        file = song["file"]
        # Validate the response
        self.assertEqual(song["id"], 1)
        self.assertEqual(file["id"], 1)
        self.assertEqual(file["name"], "BornThisWay.mp3")
        # Query DB to validate status
        song = session.query(models.Song).all()
        # Verify only one item in DB
        self.assertEqual(len(song), 1)
        # Isolate the one item in the list
        song = song[0]
        # Validate the content of the item retrieved from the DB
        self.assertEqual(song.id, 1)
        self.assertEqual(song.file_id, 1)
        self.assertEqual(song.file.name, "BornThisWay.mp3")

    def testGetSongs(self):
        """ Get a list of all the songs from a populated DB """

        # Create testing data
        # Create a couple of sample files
        fileA = models.File(name="BornThisWay.mp3")
        fileB = models.File(name="PokerFace.mp3")
        # Add them to the session and commit
        session.add_all([fileA, fileB])
        session.commit()
        # Create a couple of songs from the files
        songA = models.Song(file_id=fileA.id)
        songB = models.Song(file_id=fileB.id)
        # And add/commit
        session.add_all([songA, songB])
        session.commit()

        # Go to the page and get the response from the server, store it here
        # This is the part actually being tested
        response = self.client.get("/api/songs",
                                   headers=[("Accept", "application/json")],
                                   )

        # This is the actual test
        # Was the request to the endpoint successful?
        self.assertEqual(response.status_code, 200)
        # Did the request return a JSON object?
        self.assertEqual(response.mimetype, "application/json")
        # Decode the data using json.loads
        data = json.loads(response.data)
        # Verify that two songs have been returned
        self.assertEqual(len(data), 2)
        # Verify the contents of both songs as correct
        songA = data[0]
        self.assertEqual(songA["id"], 1)
        fileA = songA["file"]
        self.assertEqual(fileA["name"], "BornThisWay.mp3")
        songB = data[1]
        self.assertEqual(songB["id"], 2)
        fileB = songB["file"]
        self.assertEqual(fileB["name"], "PokerFace.mp3")


    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())


