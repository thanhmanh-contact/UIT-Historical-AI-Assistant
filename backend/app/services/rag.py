from app.services.embedding import get_embedding
from app.services.retrieval import search_vector_db
from app.services.llm import generate_text
from app.services.cache import get_cached_answer, set_cached_answer
from app.utils.logger import app_logger
from typing import Optional

# ─── Từ khoá nhận diện scope ───────────────────────────────────────────────────
_CNPM_KEYWORDS = [
    "cnpm", "phần mềm", "software", "khoa phần mềm",
    "software engineering", "kỹ thuật phần mềm",
    "se ", "công nghệ phần mềm", "khoa se",
]

_UIT_KEYWORDS = [
    "uit", "đại học công nghệ thông tin", "trường", "university",
    "tuyển sinh", "học phí", "campus", "cơ sở vật chất",
    "liên kết quốc tế", "nghiên cứu khoa học", "giải thưởng",
]

def detect_scope(query: str) -> str:
    """
    IMPROVEMENT: Nhận diện scope thông minh hơn với danh sách từ khoá mở rộng
    và ưu tiên từ khoá cụ thể hơn nếu cả hai đều xuất hiện.
    """
    query_lower = query.lower()

    cnpm_score = sum(1 for kw in _CNPM_KEYWORDS if kw in query_lower)
    uit_score = sum(1 for kw in _UIT_KEYWORDS if kw in query_lower)

    if cnpm_score > uit_score:
        return "cnpm"
    return "uit"  # Mặc định UIT nếu điểm bằng nhau hoặc UIT cao hơn


def generate_answer(
    query: str,
    current_scope: str = "auto",
    is_first_message: bool = True,
    conversation_history: Optional[list] = None
) -> dict:
    """
    Sinh câu trả lời RAG với hỗ trợ lịch sử hội thoại nhiều lượt.
    
    IMPROVEMENT: Thêm tham số `conversation_history` để truyền ngữ cảnh 
    các lượt hội thoại trước cho LLM.
    
    BUG FIX (cache): Cache chỉ được đọc khi KHÔNG phải lần đầu tiên, 
    nhưng vẫn được ghi bất kể. Nay tách rõ logic:
    - Không đọc cache cho lượt đầu (tránh cached greeting)
    - Không ghi cache khi có conversation_history (kết quả phụ thuộc ngữ cảnh)
    """
    # 1. Xác định scope thực tế
    scope = detect_scope(query) if current_scope == "auto" else current_scope

    # 2. Kiểm tra Cache
    # Chỉ cache khi: không phải lần đầu VÀ không có history (tránh cache kết quả phụ thuộc ngữ cảnh)
    has_history = bool(conversation_history)
    should_use_cache = not is_first_message and not has_history

    if should_use_cache:
        cached_data = get_cached_answer(query, scope)
        if cached_data:
            app_logger.info(f"✅ Cache HIT | scope={scope} | query={query[:40]}")
            return cached_data

    # 3. Embedding & Vector Search
    try:
        query_vector = get_embedding(query)
    except Exception as e:
        app_logger.error(f"❌ Lỗi embedding: {e}", exc_info=True)
        raise

    context, sources = search_vector_db(query_vector, scope)

    # 4. Sinh câu trả lời từ LLM (với ngữ cảnh hội thoại nếu có)
    llm_result = generate_text(
        query=query,
        context=context,
        scope=scope,
        is_first_message=is_first_message,
        conversation_history=conversation_history
    )

    result = {
        "answer": llm_result["answer"],
        "suggestions": llm_result["suggestions"],
        "sources": sources,
        "scope": scope,
    }

    # 5. Lưu Cache (chỉ khi không có conversation history)
    if not has_history:
        set_cached_answer(query, scope, result)

    return result
