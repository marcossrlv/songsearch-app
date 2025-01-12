from flask_cors import CORS
from flask import Flask, request
from openai import OpenAI
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/app/config/.env")
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
driver = GraphDatabase.driver(URI, auth=AUTH)
API_KEY = os.getenv("OPENAI_API_KEY")
app = Flask(__name__)
CORS(app)

def generate_embedding(chunk):
    try:
        with OpenAI(api_key=API_KEY) as clientOPENAI:
            response = clientOPENAI.embeddings.create(
                input=chunk,
                model="text-embedding-3-small"
            )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generando embeddings: {str(e)}")
        return None

def query_similar_tracks(text):
    embedding = generate_embedding(text)
    query = '''
    CALL db.index.vector.queryNodes('trackLyrics', 20, $query_embedding)
    YIELD node, score
    MATCH (t:Track)-[:CONTAINS]->(node)
    RETURN t.track_id AS track_id, node.chunk_id AS chunk_id, score
    '''
    results, result_summary, keys = driver.execute_query(query, query_embedding=embedding)
    related_tracks = []
    for record in results:
        related_tracks.append({
            "track_id": record['track_id'],
            "chunk_id": record['chunk_id'],
            "score": record['score']
        })
    return related_tracks

def group_chunks_by_track(data, n):
    track_groups = {}
    result = []
    # Agrupa los chunks que tienen el mismo track_id
    for item in data:
        track_id = item["track_id"]
        if track_id not in track_groups:
            track_groups[track_id] = []
        track_groups[track_id].append(item)
    # Agrupar tracks con nuevo score y sus chunks
    for track_id, chunks in track_groups.items():
        track_score = calculate_track_score(chunks)
        result.append({"track_id": track_id, "score": track_score, "chunks": chunks})
    result_sorted = sorted(result, key=lambda x: x["score"], reverse=True)
    return result_sorted[:n]

def calculate_track_score(track_chunks):
    base_score = track_chunks[0]["score"]  # Usar el score del primer chunk como base
    bonus = (len(track_chunks) - 1) * 0.05  # Bonificación: 5% por cada chunk adicional
    return min(base_score + bonus, 1)

def get_track_from_db(track_id):
    query = '''
    MATCH (t:Track {track_id: $track_id})
    RETURN t
    '''
    results, result_summary, keys = driver.execute_query(query, track_id=track_id)
    record = results[0]
    track = {
        "track_id": track_id,
        "title": record['t']['title'],
        "artist": record['t']['artist'],
        "cover": record['t']['cover'],
        "lyrics": record['t']['lyrics']
    }
    return track

def get_chunk_from_db(chunk_id):
    query = '''
    MATCH (c:Chunk {chunk_id: $chunk_id})
    RETURN c
    '''
    results, result_summary, keys = driver.execute_query(query, chunk_id=chunk_id)
    record = results[0]
    chunk = {
        "lyrics": record['c']['lyrics']
    }
    return chunk
    
# POST recommend
# [{id cancion, % similarity, ids chunks}]
@app.route("/recommend", methods=['POST'])
def recommend():
    data = request.get_json()
    text = data.get('text')
    similar_chunks = query_similar_tracks(text)
    results = group_chunks_by_track(similar_chunks, 5)
    return results

@app.route("/tracks/<string:track_id>")
def get_track(track_id):
    track = get_track_from_db(track_id)
    return track

@app.route("/chunks/<string:chunk_id>")
def get_chunk(chunk_id):
    chunk = get_chunk_from_db(chunk_id)
    return chunk

@app.route("/tracks/<string:track_id>/lyrics")
def get_track_lyrics(track_id):
    track = get_track_from_db(track_id)
    return track['lyrics']

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=5000)