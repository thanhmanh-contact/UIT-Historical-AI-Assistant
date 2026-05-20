"""
rag.py — RAG Pipeline chính (v2.4 — tối ưu quota API)

FIXES v2.4 (giảm số lần gọi LLM):
  ① BUG FIX CACHE: Tin nhắn đầu tiên (is_first_message=True) trước đây KHÔNG được
    cache → luôn gọi API. Đã sửa: cache hoạt động cho MỌI tin nhắn không có history.
    is_first_message được đưa vào cache key để phân biệt response có/không lời chào.

  ② LOẠI BỎ LLM PASS 2: Trước đây có thể gọi LLM 2 lần (pass 1 + Web RAG pass 2).
    Nay quyết định dùng web search TRƯỚC khi gọi LLM dựa trên độ dài context.
    Kết quả: luôn đúng 1 lần gọi LLM mỗi request (giảm 50% quota trong worst case).

  ③ CACHE EMBEDDING: embedding.py đã thêm in-memory cache → câu hỏi lặp lại không
    gọi Embedding API nữa.

Luồng xử lý (v2.4):
  1. Detect scope
  2. Kiểm tra cache (kể cả first message)
  3. Embedding (từ cache nếu có) + tìm vector DB nội bộ
  4. Nếu context không đủ → Web RAG (TRƯỚC khi gọi LLM)
  5. Gọi LLM sinh câu trả lời — CHỈ 1 LẦN DUY NHẤT
  6. Chỉ trả về sources khi LLM thực sự dùng dữ liệu đó
  7. Lưu cache
"""

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
    "hiệu trưởng", "lãnh đạo", "ban giám hiệu",
]

# Các cụm từ LLM dùng để báo "không có dữ liệu"
_NO_DATA_PHRASES = [
    "chưa cập nhật thông tin",
    "không có thông tin",
    "không tìm thấy thông tin",
    "dữ liệu chưa có",
    "nằm ngoài phạm vi dữ liệu",
    "không đủ dữ liệu",
    "không có trong tài liệu",
    "tài liệu không đề cập",
    "hiện tại mình không có",
    "không tìm thấy dữ liệu",    # ← THÊM (khớp với "hiện tại thì mình không tìm thấy dữ liệu")
    "mình không tìm thấy",        # ← THÊM
]

# Ngưỡng độ dài context nội bộ (chars) để quyết định có cần Web RAG không
# Nếu context ngắn hơn ngưỡng này → thử Web RAG TRƯỚC khi gọi LLM
_MIN_CONTEXT_CHARS = 200

# Từ khoá chỉ thông tin "hiện tại" → luôn cần web search dù DB có data cũ
_REALTIME_KEYWORDS = [
    "hiện tại", "hiện nay", "bây giờ", "năm nay", "mới nhất",
    "gần đây", "hiện tại là", "bây giờ là", "current", "latest", "now",
]

def _is_realtime_query(query: str) -> bool:
    """Phát hiện câu hỏi yêu cầu thông tin thời gian thực."""
    lower = query.lower()
    return any(kw in lower for kw in _REALTIME_KEYWORDS)


def detect_scope(query: str) -> str:
    """
    Nhận diện scope từ câu hỏi dựa trên từ khoá.
    Ưu tiên CNPM nếu score cao hơn; mặc định UIT.
    """
    query_lower = query.lower()
    cnpm_score = sum(1 for kw in _CNPM_KEYWORDS if kw in query_lower)
    uit_score  = sum(1 for kw in _UIT_KEYWORDS  if kw in query_lower)
    return "cnpm" if cnpm_score > uit_score else "uit"


def _answer_has_no_data(answer_text: str) -> bool:
    """
    Kiểm tra câu trả lời LLM có dạng 'không có dữ liệu' không.
    Dùng để quyết định có hiện sources hay không.
    """
    lower = answer_text.lower()
    return any(phrase in lower for phrase in _NO_DATA_PHRASES)


def _try_web_search(query: str, scope: str) -> tuple:
    """Helper: gọi web search, log kết quả. Trả về (context, sources)."""
    try:
        from app.services.web_search import search_uit_web
        web_context, web_sources = search_uit_web(query, scope)
        if web_context.strip():
            app_logger.info(f"Web RAG thành công: {len(web_sources)} nguồn")
            return web_context, web_sources
        else:
            app_logger.warning("Web RAG: Không lấy được nội dung từ web.")
    except Exception as e:
        app_logger.error(f"Web RAG thất bại: {e}", exc_info=True)
    return "", []


def generate_answer(
    query: str,
    current_scope: str = "auto",
    is_first_message: bool = True,
    conversation_history: Optional[list] = None,
    api_key: str = "",
) -> dict:
    """
    Sinh câu trả lời RAG hoàn chỉnh (v2.4).

    Tối ưu quota:
      - Cache hoạt động đúng kể cả first message
      - Chỉ gọi LLM đúng 1 lần mỗi request
      - Embedding được cache in-memory
    """
    # 1. Xác định scope
    scope = detect_scope(query) if current_scope == "auto" else current_scope

    # 2. Kiểm tra Cache
    #    FIX v2.4: cache cho MỌI query không có history (kể cả first message)
    #    is_first_message được đưa vào cache key → không nhầm lẫn response
    has_history = bool(conversation_history)
    # 2. Kiểm tra Cache (Redis hoặc In-process)
    cached_data = get_cached_answer(query, scope, is_first_message=is_first_message)
    if cached_data:
        app_logger.info(f"Cache HIT | scope={scope} | first={is_first_message} | query={query[:40]}")
        return cached_data

    # 3. Embedding & Vector Search (dữ liệu nội bộ)
    #    Embedding được cache in-memory trong embedding.py
    context = ""
    sources = []
    used_web = False

    try:
        query_vector = get_embedding(query, api_key=api_key)
        context, sources, found_relevant = search_vector_db(query_vector, scope)
    except Exception as e:
        app_logger.error(f"Lỗi embedding/retrieval: {e}", exc_info=True)
        found_relevant = False

    # 4. FIX v2.4: Quyết định Web RAG TRƯỚC khi gọi LLM
    #    Tiêu chí: context rỗng HOẶC quá ngắn (< _MIN_CONTEXT_CHARS)
    #    → Loại bỏ hoàn toàn Web RAG pass 2 (gọi LLM lần 2)
    # Fix: kích hoạt Web RAG khi không có chunk liên quan HOẶC context quá ngắn
    # Điều kiện kích hoạt Web RAG (sau fix đầy đủ):
    is_realtime = _is_realtime_query(query)

    if settings.WEB_SEARCH_ENABLED and (
        not found_relevant                           # Fix 1: không có chunk liên quan
        or len(context.strip()) < _MIN_CONTEXT_CHARS # Gốc: context quá ngắn
        or is_realtime                               # Fix mới: câu hỏi "hiện tại"
    ):
        reason = (
            "câu hỏi thời gian thực" if is_realtime
            else "không có chunk liên quan" if not found_relevant
            else f"context ngắn ({len(context.strip())} chars)"
        )
        app_logger.info(f"Kích hoạt Web RAG — lý do: {reason}")
        web_ctx, web_src = _try_web_search(query, scope)
        if web_ctx:
            # Ghép context nội bộ (nếu có) với web context
            context = (context.strip() + "\n\n---\n\n" + web_ctx) if context.strip() else web_ctx
            sources = sources + web_src if sources else web_src
            used_web = True

    # 5. Gọi LLM — CHỈ 1 LẦN DUY NHẤT (FIX v2.4)
    llm_result = generate_text(
        query=query,
        context=context,
        scope=scope,
        is_first_message=is_first_message,
        conversation_history=conversation_history,
        used_web=used_web,
        api_key=api_key,
    )

    answer_text = llm_result["answer"]

    # 6. Ẩn sources nếu LLM báo "không có dữ liệu"
    if _answer_has_no_data(answer_text):
        app_logger.info("LLM báo không có dữ liệu → xoá sources")
        sources = []

    result = {
        "answer":      answer_text,
        "suggestions": llm_result["suggestions"],
        "sources":     sources,
        "scope":       scope,
        "used_web":    used_web,
    }

    # 7. Lưu Cache (không cache khi dùng web RAG hoặc có conversation history)
    if not has_history and not used_web:
        set_cached_answer(query, scope, is_first_message, result)

    return result


# Import settings sau để tránh circular import
from app.config import settings
