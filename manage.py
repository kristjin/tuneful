import os
from tuneful import app
from tuneful.database import session, Base
from tuneful.models import Song, File
from flask.ext.script import Manager

manager = Manager(app)

@manager.command
def seed():
    for i in range(25):
        file = File(name="TestFile{}.mp3".format(i))
        session.add(file)
        session.commit()
        song = Song(file_id=file.id)
        session.add(song)
        session.commit()

@manager.command
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    manager.run()