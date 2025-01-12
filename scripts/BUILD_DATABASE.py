from neo4j import GraphDatabase
from requests import RequestException
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import uuid
from llama_index.core.node_parser import TokenTextSplitter
from lrclib import LrcLibAPI
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../config/.env")
SPOTIFY_CLIENT_ID = "529e6a6015224fc1b6608522cb55a352"
SPOTIFY_CLIENT_SECRET = "b3b431879f7547ecbe56d6dec0a85efb"
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"
scope = "user-library-read user-follow-read user-read-private user-top-read playlist-read-private"  # Permisos para leer la biblioteca del usuario
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=scope
))
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
driver = GraphDatabase.driver(URI, auth=AUTH)
api = LrcLibAPI(user_agent="songsearch/0.0.1")

def get_lyrics(track):
    try:
        artist = track['artist']
        title = track['title']
        results = api.search_lyrics(
        track_name=title,
        artist_name=artist
        )
        if not results:
            print(f"No se encontraron resultados para {title} de {artist}.")
            return "Letra no encontrada"
        lyrics = results[0].plain_lyrics
        return lyrics if lyrics else "Letra no encontrada"
    except RequestException as e:
        print(f"Error al buscar letra para {title} de {artist}: {e}")
        return "Error al obtener la letra"

def get_user_saved_tracks():
    tracks = []
    results = spotify.current_user_saved_tracks(limit=50)
    i = 0
    while results and i < 10:
        i += 1
        print(i)
        for item in results['items']:
            track = item['track']
            tracks.append({ 
                'track_id': str(uuid.uuid4()),
                'title': track['name'],
                'artist': track['artists'][0]['name'],
                'spotify_id': track['id'],
                'cover': track['album']['images'][0]['url'],
                'url': track['external_urls']['spotify']
            })
        results = spotify.next(results) if results['next'] else None
    return tracks

def get_user_saved_tracks_from_albums():
    tracks = []
    results = spotify.current_user_saved_albums(limit=50)
    i = 0
    while results and i < 5:
        i += 1
        print(f"Procesando lote {i}")
        for item in results['items']:
            album = item['album']
            # Obtenemos las pistas del álbum
            track_results = spotify.album_tracks(album['id'], limit=50)
            for track_item in track_results['items']:
                tracks.append({
                    'track_id': str(uuid.uuid4()),  # Generamos un ID único para la pista
                    'title': track_item['name'],  # Nombre de la pista
                    'artist': track_item['artists'][0]['name'],  # Nombre del primer artista
                    'spotify_id': track_item['id'],  # ID de la pista en Spotify
                    'url': track_item['external_urls']['spotify'],  # Enlace a la pista en Spotify
                    'cover': track_item['album']['images'][0]['url']
                })
        results = spotify.next(results) if results['next'] else None
    return tracks

def save_track_to_database(track, lyrics, chunks):
    with driver.session() as session:
        query = """
        MERGE (t:Track {track_id: $track_id})
        SET t.title = $title,
            t.artist = $artist,
            t.spotify_id = $spotify_id,
            t.lyrics = $lyrics,
            t.cover = $cover,
            t.url = $url
        """
        session.run(query, {
            "track_id": track['track_id'],
            "title": track['title'],
            "artist": track['artist'],
            "spotify_id": track['spotify_id'],
            "lyrics": lyrics,
            "cover": track['cover'],
            "url": track['url']
        })
        add_chunks_to_track(track, chunks)
        
def split_lyrics(lyrics, chunk_size, overlap):
    text_splitter = TokenTextSplitter(chunk_size, overlap)
    chunks = text_splitter.split_text(lyrics)
    chunks_with_ids = [{"chunk_id": str(uuid.uuid4()), "lyrics": chunk} for chunk in chunks]
    return chunks_with_ids

def add_chunks_to_track(track, chunks):
    query = """
    UNWIND $chunks AS chunk
    MERGE (c:Chunk {chunk_id: chunk.chunk_id})
    SET c.lyrics = chunk.lyrics
    WITH c
    MATCH (t:Track {track_id: $track_id})
    MERGE (t)-[:CONTAINS]->(c)
    """
    with driver.session() as session:
        session.run(query, chunks=chunks, track_id=track['track_id'])

def main():
    print("Getting user saved tracks...")
    user_saved_tracks = get_user_saved_tracks()
    
    print("Saving tracks to database...")
    for track in tqdm(user_saved_tracks, desc="Processing tracks", unit="track"):
        # Si aun no tiene lyrics en BBDD
        lyrics = get_lyrics(track)
        chunks = split_lyrics(lyrics, 300, 50)
        save_track_to_database(track, lyrics, chunks)
        

if __name__ == '__main__':
    main()