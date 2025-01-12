import concurrent.futures
from neo4j import GraphDatabase
from openai import OpenAI
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../config/.env")
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
driver = GraphDatabase.driver(URI, auth=AUTH)
API_KEY = os.getenv("OPENAI_API_KEY")

def get_songs_with_lyrics():
    query = """
    MATCH (t:Track)
    WHERE (t.lyrics) IS NOT NULL
    RETURN t
    """
    with driver.session() as session:
        result = session.run(query)
        return [record['t'] for record in result]
    
def get_track_chunks(track):
    query = '''
    MATCH (t:Track {track_id: $track_id})-[:CONTAINS]->(c:Chunk)
    RETURN c
    '''
    with driver.session() as session:
        result = session.run(query, track_id=track['track_id'])
        return [record['c'] for record in result]
    
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
    
def set_chunk_embedding(chunk, embedding):
    query = '''
    MATCH (c:Chunk {chunk_id: $chunk_id})
    CALL db.create.setNodeVectorProperty(c, 'embedding', $embedding)
    '''
    with driver.session() as session:
        session.run(query, chunk_id=chunk['chunk_id'], embedding=embedding)
    
def create_vector_index():
    drop_query = "DROP INDEX trackLyrics IF EXISTS;"
    query = '''CREATE VECTOR INDEX trackLyrics
        FOR (c:Chunk)
        ON c.embedding
        OPTIONS {indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
        }}'''
    driver.execute_query(drop_query)
    driver.execute_query(query)
    
def process_track(track):
    try:
        chunks = get_track_chunks(track)
        for chunk in chunks:
            try:
                lyrics = chunk['lyrics']
                embedding = generate_embedding(lyrics)
                set_chunk_embedding(chunk, embedding)
            except Exception as e:
                return f"Error al generar el embedding para el chunk {chunk}: {e}"
    except Exception as e:
        return f"Error al procesar la canción {track['title']}: {e}"


def main():
    print("Hola")
    tracks = get_songs_with_lyrics()
    total = len(tracks)
    print(f"Procesando {total} canciones.")
    # Paralelización del bucle
    with concurrent.futures.ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(process_track, tracks), total=total, desc="Processing tracks", unit="track"))
    create_vector_index()

if __name__ == '__main__':
    main()