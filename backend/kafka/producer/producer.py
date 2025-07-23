import os
from kafka import KafkaProducer
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import uuid
from tqdm import tqdm
from lrclib import LrcLibAPI
from llama_index.core.node_parser import TokenTextSplitter
from requests import RequestException
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

KAFKA_TOPIC = "songs"
KAFKA_BROKER = "kafka:9092"
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

api = LrcLibAPI(user_agent="songsearch/0.0.1")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
)

def load_playlists_from_db():
    playlists = []
    try:
        conn = psycopg2.connect(
            dbname="playlistdb",
            user="user",
            password="password",
            host="db",
            port="5432"
        )
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, last_accessed FROM playlists")
            rows = cur.fetchall()
            for row in rows:
                playlists.append({
                    "id": row[0].strip() if row[0] else None,
                    "name": row[1].strip() if row[1] else None,
                    "last_accessed": row[2] if row[2] else None
                })
    except Exception as e:
        print(f"⚠️ Error al cargar playlists desde la base de datos: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return playlists

def get_playlist_tracks(playlist_id):
    tracks = []
    try:
        results = sp.playlist_tracks(playlist_id)
        while results:
            for item in results['items']:
                track = item['track']
                tracks.append({
                    'track_id': str(uuid.uuid4()),
                    'title': track['name'],
                    'artist': track['artists'][0]['name'],
                    'spotify_id': track['id'],
                    'cover': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'url': track['external_urls']['spotify'],
                    'added_at': item['added_at']  # added date-time
                })
            results = sp.next(results) if results['next'] else None
    except spotipy.exceptions.SpotifyException as e:
        print(f"⚠️ Error al obtener canciones de la playlist {playlist_id}: {e}")
    return tracks
    
def get_lyrics(track):
    try:
        artist = track['artist']
        title = track['title']
        results = api.search_lyrics(track_name=title, artist_name=artist)
        if not results:
            print(f"No se encontraron resultados para {title} de {artist}.")
            return "Letra no encontrada"
        lyrics = results[0].plain_lyrics
        return lyrics if lyrics else "Letra no encontrada"
    except RequestException as e:
        print(f"Error al buscar letra para {title} de {artist}: {e}")
        return "Error al obtener la letra"
    
def split_lyrics(lyrics, chunk_size, overlap):
    text_splitter = TokenTextSplitter(chunk_size, overlap)
    chunks = text_splitter.split_text(lyrics)
    return [{"chunk_id": str(uuid.uuid4()), "lyrics": chunk} for chunk in chunks]

def update_last_accessed(playlist_id):
    
    API_URL = "http://api:5000"
    response = requests.patch(f"{API_URL}/playlists/{playlist_id}/update_last_accessed")
    
    if response.status_code == 200:
        print("Playlist updated:", response.json())
    else:
        print("Error updating playlist:", response.json())

def is_new_track(track, playlist_last_access):
    track_added_date = track['added_at']
    
    if playlist_last_access is None:
        return True
    
    return track_added_date > playlist_last_access 

def main():
    print("✅ Producer iniciado")
    playlists = load_playlists_from_db()
    
    for playlist in playlists:
        playlist_id = playlist['id']
        playlist_name = playlist['name']
        playlist_last_access = playlist['last_accessed']
        
        print(f"Obteniendo canciones de la playlist: {playlist_name} ({playlist_id})...")
        playlist_tracks = get_playlist_tracks(playlist_id)
        update_last_accessed(playlist_id)
                
        print("Enviando canciones al bus Kafka...")
        for track in tqdm(playlist_tracks, desc="Procesando canciones", unit="track"):
            
            """ if not is_new_track(track, playlist_last_access):
                print(f"⚠️ The track '{track['title']}' is not new. Skipping...")
                continue """
            
            lyrics = get_lyrics(track)
            chunks = split_lyrics(lyrics, 300, 50)
            
            track_data = {
                "track": track,
                "lyrics": lyrics,
                "chunks": chunks,
            }
            
            producer.send(KAFKA_TOPIC, value=track_data)
            print(f"✅ Canción '{track['title']}' enviada a Kafka.")
    
if __name__ == '__main__':
    main()