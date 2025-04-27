from flask import Blueprint, request, jsonify
from ..services.embedding import generate_embedding
from ..services.neo4j_service import query_similar_tracks, get_track_from_db, get_chunk_from_db
from ..services.utils import group_chunks_by_track

bp_recommend = Blueprint('recommend', __name__)

@bp_recommend.route("/recommend", methods=['POST'])
def recommend():
    data = request.get_json()
    embedding = generate_embedding(data.get('text'))
    raw_chunks = query_similar_tracks(embedding)
    grouped = group_chunks_by_track(raw_chunks, 5)
    return jsonify(grouped)

@bp_recommend.route("/tracks/<track_id>")
def get_track(track_id):
    t = get_track_from_db(track_id)
    return jsonify({
        "track_id": t["track_id"],
        "title": t["title"],
        "artist": t["artist"],
        "cover": t["cover"],
        "lyrics": t["lyrics"]
    })

@bp_recommend.route("/chunks/<chunk_id>")
def get_chunk(chunk_id):
    c = get_chunk_from_db(chunk_id)
    return jsonify({"lyrics": c["lyrics"]})

@bp_recommend.route("/tracks/<track_id>/lyrics")
def get_lyrics(track_id):
    t = get_track_from_db(track_id)
    return jsonify(t["lyrics"])
