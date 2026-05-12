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

def generate_answer(query: str, current_scope: str = "auto") -> dict:
    # 1. Xác định scope thực tế
    scope = detect_scope(query) if current_scope == "auto" else current_scope
    
    # 2. Kiểm tra Cache (lưu ý truyền thêm scope vào cache)
    cached_data = get_cached_answer(query, scope)
    if cached_data:
        return cached_data
        
    # 3. Embedding & Search theo Scope
    query_vector = get_embedding(query)
    context, sources = search_vector_db(query_vector, scope)
    
    # 4. Generate LLM (truyền scope vào để LLM biết nó đang đóng vai ai)
    answer = generate_text(query, context, scope)
    
    result = {
        "answer": answer,
        "sources": sources,
        "scope": scope # Trả về scope để Frontend biết đổi màu UI
    }
    
    set_cached_answer(query, scope, result)
    return result