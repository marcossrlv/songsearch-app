import requests
import jwt
from flask import current_app
from ..models.user import db, User
import datetime

def exchange_code_for_token(code):
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': current_app.config['SPOTIFY_REDIRECT_URI'],
        'client_id': current_app.config['SPOTIFY_CLIENT_ID'],
        'client_secret': current_app.config['SPOTIFY_CLIENT_SECRET'],
    }

    res = requests.post("https://accounts.spotify.com/api/token", data=payload)

    # 💡 Add error logging
    if res.status_code != 200:
        print("Failed to exchange code:", res.status_code, res.text)

    return res.json()


def get_spotify_user(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get("https://api.spotify.com/v1/me", headers=headers)
    return res.json()

def find_or_create_user(spotify_user):
    user = User.query.filter_by(spotify_id=spotify_user['id']).first()

    if not user:
        user = User(
            spotify_id=spotify_user['id'],
            email=spotify_user.get('email'),
            display_name=spotify_user.get('display_name')
        )
        db.session.add(user)
        db.session.commit()

    return user


def generate_jwt(user):
    payload = {
        'spotify_id': user.spotify_id,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')
    
    # Ensure token is returned as string
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return token

def verify_jwt(token: str):
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=["HS256"]
        )
        print("Decoded JWT:", payload)
        return payload
    except jwt.ExpiredSignatureError:
        print("JWT expired")
        return None
    except jwt.InvalidTokenError as e:
        print("Invalid JWT:", str(e))
        return None

