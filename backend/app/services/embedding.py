"""
embedding.py — Google Gemini Embedding Service
"""

from app.config import settings
from app.utils.logger import app_logger

def _get_client(api_key: str = ""):
    """Khởi tạo Gemini client với key tùy chọn."""
    key = api_key or settings.GOOGLE_API_KEY
    if not key:
        raise RuntimeError("Không có API Key nào khả dụng.")
    
    from google import genai
    from google.genai import types
    return genai.Client(
        api_key=key,
        http_options=types.HttpOptions(api_version="v1beta"),
    )

def get_embedding(text: str, api_key: str = "") -> list:
    """Tạo vector embedding, có hỗ trợ fallback nếu key lỗi."""
    from google.genai import types

    text = text.replace("\n", " ").strip()
    if not text:
        raise ValueError("Văn bản trống.")

    # Thử lần 1: Dùng key truyền vào (User Key) hoặc Server Key
    try:
        client = _get_client(api_key)
        response = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        return response.embeddings[0].values
    except Exception as e:
        # Nếu dùng User Key mà lỗi, thử lại lần 2 bằng Server Key (nếu khác nhau)
        if api_key and api_key != settings.GOOGLE_API_KEY:
            app_logger.warning(f"User API Key lỗi ({e}), đang thử lại bằng Server Key...")
            try:
                client = _get_client(settings.GOOGLE_API_KEY)
                response = client.models.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    contents=text,
                    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
                )
                return response.embeddings[0].values
            except Exception as e2:
                app_logger.error(f"Cả 2 API Key đều lỗi: {e2}")
                raise RuntimeError("Hệ thống AI hiện đang tạm ngưng do lỗi API Key.")
        
        app_logger.error(f"Lỗi Embedding: {e}")
        raise RuntimeError(f"Không thể tạo embedding: {e}")
