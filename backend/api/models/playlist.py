from . import db

class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
