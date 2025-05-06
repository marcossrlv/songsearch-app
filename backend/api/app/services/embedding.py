from openai import OpenAI
from config import Config

api_key = Config.OPENAI_API_KEY

def generate_embedding(chunk):
    try:
        with OpenAI(api_key=api_key) as client:
            response = client.embeddings.create(
                input=chunk,
                model="text-embedding-3-small"
            )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None
