import faiss
import json
import numpy as np
from app.config import settings
from app.utils.logger import app_logger

# Lưu trữ 2 DB trên RAM
dbs = {
    "uit": {"index": None, "chunks": []},
    "cnpm": {"index": None, "chunks":[]}
}

def load_all_dbs():
    try:
        # Load UIT
        dbs["uit"]["index"] = faiss.read_index(settings.FAISS_UIT_PATH)
        with open(settings.DATA_UIT_PATH, "r", encoding="utf-8") as f:
            dbs["uit"]["chunks"] = json.load(f)
            
        # Load CNPM
        dbs["cnpm"]["index"] = faiss.read_index(settings.FAISS_CNPM_PATH)
        with open(settings.DATA_CNPM_PATH, "r", encoding="utf-8") as f:
            dbs["cnpm"]["chunks"] = json.load(f)
            
        app_logger.info("✅ Đã tải thành công 2 DB: UIT và CNPM")
    except Exception as e:
        app_logger.error(f"⚠️ Lỗi load DB: {e}")

load_all_dbs()

def search_vector_db(query_vector: list, scope: str, top_k: int = None):
    """Tìm kiếm trong DB cụ thể (uit hoặc cnpm)"""
    if top_k is None:
        top_k = settings.TOP_K_RETRIEVAL
    
    db = dbs.get(scope)
    if not db["index"]: return "", []

    vector_np = np.array([query_vector]).astype("float32")
    distances, indices = db["index"].search(vector_np, top_k)
    
    context_parts = []
    sources = []
    for i in indices[0]:
        if i != -1 and i < len(db["chunks"]):
            chunk = db["chunks"][i]
            context_parts.append(chunk["text"])
            if chunk["metadata"] not in sources:
                sources.append(chunk["metadata"])
                
    return " \n".join(context_parts), sources