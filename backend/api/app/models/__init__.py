from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .playlist import Playlist  # Add other models here as needed
