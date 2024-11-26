from flask_cors import CORS
from flask import Flask, request
import chromadb
from openai import OpenAI
from spotipy.oauth2 import SpotifyOAuth
import spotipy

API_KEY = "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"
chroma_client = chromadb.HttpClient(host='localhost', port=8000)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="529e6a6015224fc1b6608522cb55a352",
                                               client_secret="b3b431879f7547ecbe56d6dec0a85efb",
                                               redirect_uri="http://localhost:8888",
                                               scope="user-library-read user-follow-read user-read-private user-read-email user-top-read"))

app = Flask(__name__)
CORS(app)

@app.route("/", methods=['POST'])
def hello_world():
    data = request.get_json()
    text = data.get('text')
    results = query_music(text)
    id_list = results['ids'][0]
    scores = results['distances'][0]
    texts = results['documents'][0]
    clean_list = clean_ids(id_list)
    spotify_data = get_songs_data(clean_list)
    relevant_data = []
    for i, item in enumerate(spotify_data):
        relevant_data.append({
            'name':item['name'],
            'artist':item['artists'][0]['name'],
            'score':scores[i],
            'image':item['album']['images'][0]['url'],
            'url':item['external_urls']['spotify']
        })
    relevant_data.reverse()
    return relevant_data

def get_songs_data(id_list):
    tracks = []
    for song_id in id_list:
        tracks.append(sp.track(song_id))
    return tracks

# En un futuro esto no hará falta, cuando los embeddings estén bien hechos
def clean_ids(id_list):
    new_id_list = []
    for item in id_list:
        new_id_list.append(item.split("_")[0])
    return new_id_list

def query_music(input_text):
    collection = chroma_client.get_collection(name='song_lyrics')
    embedded_query = generate_embedding(input_text)
    results = collection.query(
        query_embeddings=embedded_query,
        n_results=5
    )
    return results
    
def generate_embedding(text):
    """
    Genera embeddings usando el cliente de OpenAI.
    """
    try:
        with OpenAI(api_key=API_KEY) as clientOPENAI:
            response = clientOPENAI.embeddings.create(
                input=text,
                model="text-embedding-3-large"
            )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generando embeddings: {str(e)}")
        return None