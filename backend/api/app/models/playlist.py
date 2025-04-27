from . import db
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime, timezone

class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    last_accessed = db.Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Method to update last_accessed_at to the current timestamp with time zone
    @classmethod
    def update_last_accessed(cls, playlist_id):
        playlist = cls.query.get(playlist_id)  # Retrieve the playlist by its ID
        if playlist:
            playlist.last_accessed = datetime.now(timezone.utc)  # Set the current time in UTC
            db.session.commit()  # Commit the changes to the database
            return playlist
        else:
            return None  # Playlist not found
