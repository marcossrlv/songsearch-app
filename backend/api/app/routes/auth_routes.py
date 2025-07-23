from flask import Blueprint, request, redirect, current_app, jsonify
from urllib.parse import urlencode
from ..services import auth_service

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login")
def login():
    query_params = urlencode({
        "client_id": current_app.config["SPOTIFY_CLIENT_ID"],
        "response_type": "code",
        "redirect_uri": current_app.config["SPOTIFY_REDIRECT_URI"],
        "scope": "user-read-email",
        "state": request.args.get("next", "http://localhost:3000")  # optional: redirect target
    })

    return redirect(f"https://accounts.spotify.com/authorize?{query_params}")

@auth_bp.route("/callback")
def callback():
    try:
        code = request.args.get("code")
        state = request.args.get("state")
        print("Received code:", code)
        print("Received state:", state)

        token_data = auth_service.exchange_code_for_token(code)
        print("Token data:", token_data)

        access_token = token_data.get("access_token")
        if not access_token:
            return jsonify({"error": "Failed to get access token", "details": token_data}), 400

        spotify_user = auth_service.get_spotify_user(access_token)
        print("Spotify user:", spotify_user)

        user = auth_service.find_or_create_user(spotify_user)
        token = auth_service.generate_jwt(user)
        print("Generated JWT token:", token)

        redirect_url = f"{state}?token={token}" if state else f"http://localhost:3000?token={token}"
        return redirect(redirect_url)

    except Exception as e:
        print("Error in /callback:", str(e))
        return jsonify({"error": "Server error", "details": str(e)}), 500

