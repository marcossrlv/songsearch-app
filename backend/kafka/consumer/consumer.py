from kafka import KafkaConsumer
from neo4j import GraphDatabase
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Carga de variables de entorno
KAFKA_TOPIC = "songs"
KAFKA_BROKER = "kafka:9092"
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
API_KEY = os.getenv("OPENAI_API_KEY")

# Conectar a Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_vector_index():
    query = '''CREATE VECTOR INDEX trackLyrics IF NOT EXISTS
        FOR (c:Chunk)
        ON c.embedding
        OPTIONS {indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
        }}'''
    driver.execute_query(query)
    
create_vector_index()

def track_exists(spotify_id):
    with driver.session() as session:
        result = session.run("""
            MATCH (t:Track {spotify_id: $spotify_id})
            RETURN t
        """, {"spotify_id": spotify_id})
        return result.peek() is not None

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
        
def generate_embedding(chunk_lyrics):
    try:
        with OpenAI(api_key=API_KEY) as clientOPENAI:
            response = clientOPENAI.embeddings.create(
                input=chunk_lyrics,
                model="text-embedding-3-small"
            )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generando embeddings: {str(e)}")
        return None
    
def set_chunk_embedding(chunk, embedding):
    query = '''
    MATCH (c:Chunk {chunk_id: $chunk_id})
    CALL db.create.setNodeVectorProperty(c, 'embedding', $embedding)
    '''
    with driver.session() as session:
        session.run(query, chunk_id=chunk['chunk_id'], embedding=embedding)
        
def process_track(track, chunks):
    try:
        for chunk in chunks:
            try:
                lyrics = chunk['lyrics']
                embedding = generate_embedding(lyrics)
                set_chunk_embedding(chunk, embedding)
            except Exception as e:
                return f"Error al generar el embedding para el chunk {chunk}: {e}"
    except Exception as e:
        return f"Error al procesar la canción {track['title']}: {e}"
    
def is_newly_added_track(track, playlist_last_access):
    track_added_date = track['added_at']
    
    if playlist_last_access is None:
        return True
    
    return track_added_date > playlist_last_access        

def consumer():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='test-group',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    
    print("📥 Esperando mensajes de Kafka...")
    for message in consumer:
        data = message.value
        track = data.get("track")
        lyrics = data.get("lyrics")
        chunks = data.get("chunks")

        if track and lyrics is not None and chunks is not None:
            print(f"🎵 Procesando canción: {track['title']} de {track['artist']}")
            
            if track_exists(track['spotify_id']):
                print(f"⚠️ The song '{track['title']}' is already in DB. Skipping...")
                continue
            
            save_track_to_database(track, lyrics, chunks)
            process_track(track, chunks)
            print(f"✅ Canción '{track['title']}' guardada en Neo4j.")
        else:
            print("⚠️ Mensaje recibido con datos incompletos:", data)

if __name__ == "__main__":
    consumer()