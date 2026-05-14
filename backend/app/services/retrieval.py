import faiss
import json
import numpy as np
from app.config import settings
from app.utils.logger import app_logger

# Lưu trữ 2 DB trên RAM
dbs = {
    "uit": {"index": None, "chunks": []},
    "cnpm": {"index": None, "chunks": []}
}

def load_all_dbs():
    """Tải toàn bộ FAISS index và chunk data vào RAM."""
    errors = []
    try:
        dbs["uit"]["index"] = faiss.read_index(settings.FAISS_UIT_PATH)
        with open(settings.DATA_UIT_PATH, "r", encoding="utf-8") as f:
            dbs["uit"]["chunks"] = json.load(f)
        app_logger.info(f"✅ Đã tải DB UIT: {dbs['uit']['index'].ntotal} vectors")
    except Exception as e:
        errors.append(f"UIT: {e}")
        app_logger.error(f"⚠️ Lỗi load DB UIT: {e}")

    try:
        dbs["cnpm"]["index"] = faiss.read_index(settings.FAISS_CNPM_PATH)
        with open(settings.DATA_CNPM_PATH, "r", encoding="utf-8") as f:
            dbs["cnpm"]["chunks"] = json.load(f)
        app_logger.info(f"✅ Đã tải DB CNPM: {dbs['cnpm']['index'].ntotal} vectors")
    except Exception as e:
        errors.append(f"CNPM: {e}")
        app_logger.error(f"⚠️ Lỗi load DB CNPM: {e}")

    return errors

def get_db_status() -> dict:
    """Trả về trạng thái các DB để dùng cho health check."""
    return {
        "uit": {
            "loaded": dbs["uit"]["index"] is not None,
            "total_vectors": dbs["uit"]["index"].ntotal if dbs["uit"]["index"] is not None else 0,
            "total_chunks": len(dbs["uit"]["chunks"])
        },
        "cnpm": {
            "loaded": dbs["cnpm"]["index"] is not None,
            "total_vectors": dbs["cnpm"]["index"].ntotal if dbs["cnpm"]["index"] is not None else 0,
            "total_chunks": len(dbs["cnpm"]["chunks"])
        }
    }

def search_vector_db(query_vector: list, scope: str, top_k: int = None) -> tuple[str, list]:
    """
    Tìm kiếm trong vector DB theo scope và lọc kết quả theo ngưỡng độ tương đồng.
    
    BUG FIX: `if not db["index"]` luôn là False với FAISS index object (object truthy).
    Đã sửa thành `if db["index"] is None`.
    
    IMPROVEMENT: Thêm similarity threshold để lọc kết quả không liên quan.
    FAISS trả về L2 distance — giá trị càng nhỏ = càng liên quan.
    """
    if top_k is None:
        top_k = settings.TOP_K_RETRIEVAL

    db = dbs.get(scope)
    
    # BUG FIX: phải dùng `is None`, không phải `not db["index"]`
    if db is None or db["index"] is None:
        app_logger.warning(f"⚠️ DB '{scope}' chưa được tải hoặc không tồn tại.")
        return "", []

    vector_np = np.array([query_vector]).astype("float32")
    distances, indices = db["index"].search(vector_np, top_k)

    context_parts = []
    sources = []
    filtered_count = 0

    for dist, i in zip(distances[0], indices[0]):
        # IMPROVEMENT: Lọc kết quả quá xa (không liên quan)
        # Ngưỡng L2 distance — tuỳ chỉnh trong config nếu cần
        if i == -1 or i >= len(db["chunks"]):
            continue
        if dist > settings.SIMILARITY_THRESHOLD:
            filtered_count += 1
            continue

        chunk = db["chunks"][i]
        context_parts.append(chunk["text"])
        metadata = chunk.get("metadata")
        if metadata and metadata not in sources:
            sources.append(metadata)

    if filtered_count > 0:
        app_logger.info(f"🔍 Đã lọc {filtered_count} chunk không đủ liên quan (scope={scope})")

    if not context_parts:
        app_logger.warning(f"⚠️ Không tìm thấy chunk nào đủ liên quan cho scope={scope}")

    return "\n\n".join(context_parts), sources

# Tải DB khi module được import
load_errors = load_all_dbs()
if load_errors:
    app_logger.warning(f"⚠️ Một số DB chưa được tải: {load_errors}. Hãy chạy scripts/init_data.py trước.")
