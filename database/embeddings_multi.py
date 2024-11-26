import chromadb
from llama_index.core.node_parser import TokenTextSplitter
from openai import OpenAI
import csv, sys
import pandas as pd
from tqdm import tqdm
import multiprocessing

API_KEY = "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"
file_path = 'lyrics.csv'
csv.field_size_limit(sys.maxsize)
client = chromadb.HttpClient(host='localhost', port=8000)

def split_lyrics(lyrics, chunk_size, overlap):
    text_splitter = TokenTextSplitter(chunk_size, overlap)
    chunks = text_splitter.split_text(lyrics)
    return chunks

def generate_embeddings(chunk):
    """
    Genera embeddings usando el cliente de OpenAI.
    """
    try:
        with OpenAI(api_key=API_KEY) as clientOPENAI:
            response = clientOPENAI.embeddings.create(
                input=chunk,
                model="text-embedding-3-large"
            )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generando embeddings: {str(e)}")
        return None

def process_song(row):
    """
    Procesa una canción para generar embeddings y almacenarlos en ChromaDB.
    """
    try:
        collection = client.get_or_create_collection(
            name="song_lyrics",
            metadata={"hnsw:space": "cosine"}
        )

        song_id = row["song_id"]
        lyrics = row["lyrics"]

        # Verificar que las letras no sean nulas y sean del tipo correcto
        if pd.isna(lyrics) or not isinstance(lyrics, str):
            return f"Advertencia: La canción con ID {song_id} tiene letras inválidas. Se omite."

        # Dividir las letras en chunks
        chunks = split_lyrics(lyrics, 300, 90)

        # Generar embeddings
        embeddings = [generate_embeddings(chunk) for chunk in chunks]

        # Agregar chunks y embeddings a ChromaDB
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            collection.add(
                documents=[chunk],
                metadatas=[{"song_id": song_id, "chunk_index": i}],
                ids=[f"{song_id}_{i}"],
                embeddings=[embedding],
            )
        return f"Canción con ID {song_id} procesada correctamente."
    except Exception as e:
        return f"Error procesando la canción con ID {row['song_id']}: {str(e)}"

def main():
    df = pd.read_csv(
        file_path,
        delimiter='\t',  # Cambia a ',' si ese es el delimitador
        quotechar='"',
        escapechar='\\',
        engine='python',
    )
    
    total_songs = len(df)
    
    # Crear pool de procesos
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        # Procesar canciones en paralelo
        results = list(tqdm(pool.imap_unordered(process_song, df.to_dict(orient="records")), 
                            total=total_songs, desc="Procesando canciones", unit="canción"))
        
    for result in results:
        print(result)

    print("¡Embeddings generados y almacenados en ChromaDB!")

if __name__ == '__main__':
    main()
