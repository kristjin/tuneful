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
        # Verify that two posts have been returned
        self.assertEqual(len(data), 2)
        # Verify the contents of both posts as correct
        songA = data[0]
        self.assertEqual(songA["id"], 1)
        # self.assertEqual(songA, "")
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


