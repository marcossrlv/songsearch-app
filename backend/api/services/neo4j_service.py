from neo4j import GraphDatabase
from config import Config

NEO4J_URI = Config.NEO4J_URI
NEO4J_AUTH = Config.NEO4J_AUTH
driver = GraphDatabase.driver("bolt://neo4j:7687", auth=NEO4J_AUTH)

def query_similar_tracks(embedding):
    query = '''
    CALL db.index.vector.queryNodes('trackLyrics', 20, $query_embedding)
    YIELD node, score
    MATCH (t:Track)-[:CONTAINS]->(node)
    RETURN t.track_id AS track_id, node.chunk_id AS chunk_id, score
    '''
    results, _, _ = driver.execute_query(query, query_embedding=embedding)
    return results

def get_track_from_db(track_id):
    query = 'MATCH (t:Track {track_id: $track_id}) RETURN t'
    results, _, _ = driver.execute_query(query, track_id=track_id)
    return results[0]['t']

def get_chunk_from_db(chunk_id):
    query = 'MATCH (c:Chunk {chunk_id: $chunk_id}) RETURN c'
    results, _, _ = driver.execute_query(query, chunk_id=chunk_id)
    return results[0]['c']
