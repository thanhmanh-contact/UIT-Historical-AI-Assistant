from google import genai
from google.genai import types
from app.config import settings
from app.utils.logger import app_logger

client = genai.Client(
    api_key=settings.GOOGLE_API_KEY,
    http_options=types.HttpOptions(api_version="v1beta")
)


def get_embedding(text: str) -> list:
    """
    Tạo vector embedding từ văn bản đầu vào.

    BUG FIX: Thêm try/except với thông báo lỗi rõ ràng thay vì để exception
    lan truyền không kiểm soát lên tầng API (gây lỗi 500 mờ nhạt).
    """
    text = text.replace("\n", " ").strip()
    if not text:
        raise ValueError("Văn bản đầu vào không được trống khi tạo embedding.")

    try:
        response = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            )
        )
        return response.embeddings[0].values
    except Exception as e:
        app_logger.error(f"❌ Lỗi Embedding API: {e}", exc_info=True)
        # Re-raise để tầng trên (rag.py) bắt và xử lý đúng cách
        raise RuntimeError(f"Không thể tạo embedding: {e}") from e
