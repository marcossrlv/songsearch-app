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

# Configuración
KAFKA_TOPIC = "songs"
KAFKA_BROKER = "kafka:9092"
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

api = LrcLibAPI(user_agent="songsearch/0.0.1")

# Conectar a Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

# Productor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
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
            cur.execute("SELECT id, name FROM playlists")
            rows = cur.fetchall()
            for row in rows:
                playlists.append({
                    "id": row[0].strip(),
                    "name": row[1].strip()
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
                    'url': track['external_urls']['spotify']
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

def main():
    print("✅ Producer iniciado")
    #playlists = []
    playlists = load_playlists_from_db()
    
    for playlist in playlists:
        playlist_id = playlist['id']
        playlist_name = playlist['name']
        
        print(f"Obteniendo canciones de la playlist: {playlist_name} ({playlist_id})...")
        playlist_tracks = get_playlist_tracks(playlist_id)
        
        print("Enviando canciones al bus Kafka...")
        for track in tqdm(playlist_tracks, desc="Procesando canciones", unit="track"):
            
            lyrics = get_lyrics(track)
            chunks = split_lyrics(lyrics, 300, 50)
            
            track_data = {
                "track": track,
                "lyrics": lyrics,
                "chunks": chunks
            }
            
            producer.send(KAFKA_TOPIC, value=track_data)
            print(f"✅ Canción '{track['title']}' enviada a Kafka.")
    
if __name__ == '__main__':
    main()