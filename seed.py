import os
from tuneful import app
from tuneful.database import session, Base
from tuneful.models import Song, File
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


class DB(object):
    def __init__(self, metadata):
        self.metadata = metadata

manager = Manager(app)
migrate = Migrate(app, DB(Base.metadata))
manager.add_command('db', MigrateCommand)

@manager.command
def seed():
    for i in range(25):
        file = File(name="TestFile{}.mp3".format(i))
        session.add(file)
        session.commit()
        song = Song(file_id=file.id)
        session.add(song)
        session.commit()
