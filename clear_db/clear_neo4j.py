from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../config/.env")

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    # Función para borrar todos los datos de la base de datos
    def clear_database(self):
        with self.driver.session() as session:
            # Eliminar relaciones
            session.run("MATCH ()-[r]->() DELETE r")
            # Eliminar nodos
            session.run("MATCH (n) DELETE n")
            print("Base de datos borrada.")

# Función para obtener las credenciales y URI de la base de datos desde variables de entorno
def get_neo4j_credentials():
    uri = os.getenv("NEO4J_URI")  # Usa el valor por defecto si no se encuentra en el entorno
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    return uri, user, password

# Función principal que ejecuta el proceso de limpieza
def main():
    uri, user, password = get_neo4j_credentials()
    conn = Neo4jConnection(uri, user, password)
    conn.clear_database()  # Borra la base de datos
    conn.close()  # Cierra la conexión

if __name__ == "__main__":
    main()
