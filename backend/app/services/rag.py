from app.services.embedding import get_embedding
from app.services.retrieval import search_vector_db
from app.services.llm import generate_text
from app.services.cache import get_cached_answer, set_cached_answer

def detect_scope(query: str) -> str:
    """Tự động phân loại câu hỏi nếu user nhập từ màn hình Home"""
    query_lower = query.lower()
    if "cnpm" in query_lower or "phần mềm" in query_lower or "software" in query_lower:
        return "cnpm"
    return "uit" # Mặc định là UIT nếu không detect được

def generate_answer(query: str, current_scope: str = "auto", is_first_message: bool = True) -> dict:
    # 1. Xác định scope thực tế
    scope = detect_scope(query) if current_scope == "auto" else current_scope

    # 2. Kiểm tra Cache (chỉ cache khi không phải lần đầu để tránh cached greeting)
    cached_data = get_cached_answer(query, scope)
    if cached_data and not is_first_message:
        return cached_data

    # 3. Embedding & Search theo Scope
    query_vector = get_embedding(query)
    context, sources = search_vector_db(query_vector, scope)

    # 4. Generate LLM
    llm_result = generate_text(query, context, scope, is_first_message)

    result = {
        "answer": llm_result["answer"],
        "suggestions": llm_result["suggestions"],
        "sources": sources,
        "scope": scope,
    }
    
    set_cached_answer(query, scope, result)
    return result