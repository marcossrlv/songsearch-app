import csv
import sys
from neomodel import StructuredNode, StringProperty, config
import pandas as pd

config.DATABASE_URL = 'bolt://neo4j:HGXaKq_zWLWvG7p@localhost:7687'

# Define el modelo para una canción
class Song(StructuredNode):
    spotify_id = StringProperty(unique_index=True, required=True)
    lyrics = StringProperty()

# Carga el archivo CSV
file_path = 'lyrics.csv'

# Incrementa el límite del tamaño de campo
csv.field_size_limit(sys.maxsize)

def main():
    df = pd.read_csv(
        file_path,
        delimiter='\t',  # Cambia a ',' si ese es el delimitador
        quotechar='"',
        escapechar='\\',
        engine='python',
    )
    print(df.head())
    for index, row in df.iterrows():
        created = Song.get_or_create({
            "spotify_id":row['song_id'], "lyrics":row['lyrics']
        })
        if created:
            print(f"Song {row['song_id']} created")
        else:
            print(f"Song {row['song_id']} already exists")

if __name__ == '__main__':
    main()