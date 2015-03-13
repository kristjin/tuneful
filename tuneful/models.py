import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from database import Base, engine

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)

    def as_dictionary(self):
        song = {
            "id": self.id,
            "file": {
                "id": self.file.id,
                "name": self.file.name
            }
        }
        return song

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    song = relationship("Song", uselist=False, backref="file")

    def as_dictionary(self):
        return {
            "id": self.id,
            "name": self.name,
            "path": url_for("uploaded_file", filename=self.name)
        }