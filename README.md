# SongSearch 
SongSearch is a semantic search engine designed for music enthusiasts. It empowers users to discover songs by exploring concepts, narratives, or emotions, offering a more intuitive and meaningful search experience beyond traditional text-based methods.

# How to run it
1. Clone the repository
```bash
git clone https://github.com/marcossrlv/songsearch_app.git
cd songsearch_app
```
You will need to add the following variables inside backend/.env file:
- OPENAI_API_KEY
- SPOTIFY_CLIENT_ID
- SPOTIFY_CLIENT_SECRET

2. Make sure you already have Docker and Docker Compose installed on your machine.
3. Start the services with Docker Compose
```bash
docker-compose -f up --build
```

4. Access the app:
- **UI**: [http://localhost:3000](http://localhost:3000)
- **API**: [http://localhost:5001](http://localhost:5001)
- **Neo4j**: [http://localhost:7474](http://localhost:7474) (no auth)

That's it! You can now explore SongSearch and enjoy its features.

