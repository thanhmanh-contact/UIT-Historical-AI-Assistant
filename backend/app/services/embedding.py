from google import genai
from google.genai import types
from app.config import settings

client = genai.Client(
    api_key=settings.GOOGLE_API_KEY,
    http_options=types.HttpOptions(api_version="v1beta")
)
    
def get_embedding(text: str) -> list:
    """Sử dụng Gemini Embedding 2 (Mới nhất và mạnh nhất)"""
    text = text.replace("\n", " ").strip()
    
    # Gọi API
    response = client.models.embed_content(
        model=settings.EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )
    )
    
    return response.embeddings[0].values