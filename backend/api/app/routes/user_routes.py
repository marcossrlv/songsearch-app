from flask import Blueprint, request, jsonify
import requests
from ..services import auth_service

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/playlists")
def get_playlists():
    # Step 1: Extract token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization token missing or invalid"}), 401

    jwt_token = auth_header.split(" ")[1]

    # Step 2: Decode and verify JWT
    user = auth_service.verify_jwt(jwt_token)
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 401

    # Step 3: Get Spotify access token for user
    access_token = auth_service.get_access_token_for_user(user["id"])
    if not access_token:
        return jsonify({"error": "Spotify access token not found"}), 400

    # Step 4: Call Spotify API
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch playlists", "details": response.json()}), response.status_code

    return jsonify(response.json())
