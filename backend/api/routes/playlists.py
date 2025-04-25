from flask import Blueprint, request, jsonify
from models.playlist import Playlist
from models import db

bp_playlists = Blueprint('playlists', __name__)

@bp_playlists.route("/playlists", methods=["GET"])
def get_playlists():
    playlists = Playlist.query.all()
    return jsonify([{"id": p.id, "name": p.name} for p in playlists])

@bp_playlists.route("/playlists", methods=["POST"])
def add_playlist():
    data = request.get_json()
    if not data or not data.get("id") or not data.get("name"):
        return jsonify({"error": "Invalid payload"}), 400
    if Playlist.query.get(data["id"]):
        return jsonify({"error": "Playlist with that ID already exists"}), 409
    new_playlist = Playlist(id=data["id"], name=data["name"])
    db.session.add(new_playlist)
    db.session.commit()
    return jsonify({"id": new_playlist.id, "name": new_playlist.name}), 201

@bp_playlists.route("/playlists/<string:playlist_id>", methods=["DELETE"])
def delete_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    db.session.delete(playlist)
    db.session.commit()
    return jsonify({"message": "Playlist deleted"})
