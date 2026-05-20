"""
retrieval.py — FAISS Vector Search

BUG FIX: `if not db["index"]` luôn False với FAISS object → đổi sang `is None`.
v2.3: Cải thiện log khi DB chưa được tạo, phân biệt "file không tồn tại" vs lỗi khác.
"""

import faiss
import json
import numpy as np
from app.config import settings
from app.utils.logger import app_logger

dbs = {
    "uit":  {"index": None, "chunks": []},
    "cnpm": {"index": None, "chunks": []},
}


def load_all_dbs():
    """Tải toàn bộ FAISS index và chunk data vào RAM khi khởi động."""
    errors = []

    for scope, faiss_path, data_path in [
        ("uit",  settings.FAISS_UIT_PATH,  settings.DATA_UIT_PATH),
        ("cnpm", settings.FAISS_CNPM_PATH, settings.DATA_CNPM_PATH),
    ]:
        try:
            dbs[scope]["index"] = faiss.read_index(faiss_path)
            with open(data_path, "r", encoding="utf-8") as f:
                dbs[scope]["chunks"] = json.load(f)
            app_logger.info(
                f"✅ Đã tải DB {scope.upper()}: "
                f"{dbs[scope]['index'].ntotal} vectors, "
                f"{len(dbs[scope]['chunks'])} chunks"
            )
        except FileNotFoundError:
            errors.append(f"{scope.upper()}: File chưa tồn tại ({faiss_path})")
            app_logger.warning(
                f"⚠️  DB {scope.upper()} chưa được tạo. "
                f"Chạy: python scripts/init_data.py --scope {scope}"
            )
        except Exception as e:
            errors.append(f"{scope.upper()}: {e}")
            app_logger.error(f"❌ Lỗi load DB {scope.upper()}: {e}", exc_info=True)

    return errors


def get_db_status() -> dict:
    return {
        scope: {
            "loaded":        dbs[scope]["index"] is not None,
            "total_vectors": dbs[scope]["index"].ntotal if dbs[scope]["index"] is not None else 0,
            "total_chunks":  len(dbs[scope]["chunks"]),
        }
        for scope in ("uit", "cnpm")
    }


def _extract_source_info(metadata) -> dict | None:
    if metadata is None:
        return None
    if isinstance(metadata, dict):
        if "url" not in metadata:
            metadata["url"] = metadata.get("source", metadata.get("link", ""))
        metadata.setdefault("source_type", "local")
        return metadata
    if isinstance(metadata, str) and metadata.strip():
        return {"url": metadata.strip(), "title": metadata.strip(), "source_type": "local"}
    return None


def search_vector_db(query_vector: list, scope: str, top_k: int = None) -> tuple:
    """
    Tìm kiếm trong FAISS vector DB theo scope, lọc theo similarity threshold.

    Returns:
        (context_text, sources_list)
    """
    if top_k is None:
        top_k = settings.TOP_K_RETRIEVAL

    db = dbs.get(scope)
    if db is None or db["index"] is None:
        app_logger.warning(
            f"⚠️  DB '{scope}' chưa được tải — "
            f"chạy: python scripts/init_data.py --scope {scope}"
        )
        return "", []

    vector_np = np.array([query_vector]).astype("float32")
    distances, indices = db["index"].search(vector_np, top_k)

    context_parts = []
    sources = []
    filtered_count = 0
    found_relevant = False      # ← THÊM

    for dist, i in zip(distances[0], indices[0]):
        if i == -1 or i >= len(db["chunks"]):
            continue
        if dist > settings.SIMILARITY_THRESHOLD:
            filtered_count += 1
            continue

        found_relevant = True   # ← THÊM: chỉ True khi có chunk pass threshold
        chunk = db["chunks"][i]
        text = chunk.get("text", "").strip()
        if not text:
            continue

        context_parts.append(text)

        src_info = _extract_source_info(chunk.get("metadata"))
        if src_info and src_info not in sources:
            sources.append(src_info)

    if filtered_count > 0:
        app_logger.info(
            f"🔍 Đã lọc {filtered_count}/{top_k} chunk không đủ liên quan "
            f"(scope={scope}, threshold={settings.SIMILARITY_THRESHOLD})"
        )

    if not context_parts:
        app_logger.info(f"📭 Không có chunk nào vượt ngưỡng cho scope={scope}")

    return "\n\n".join(context_parts), sources, found_relevant  # ← THÊM found_relevant


# Tải DB khi module được import
load_errors = load_all_dbs()
if load_errors:
    app_logger.warning(
        f"⚠️  Một số DB chưa được tải: {load_errors}. "
        "Web RAG fallback sẽ được dùng khi cần."
    )
