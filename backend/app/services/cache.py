import redis
import hashlib
import json
from app.config import settings
from app.utils.logger import app_logger
from app.utils.sanitize import is_error_response

# ── Kết nối Redis ──────────────────────────────────────────────────────────────
# Trong backend/app/services/cache.py
try:
    # Kết nối Upstash qua URL (Hỗ trợ cả SSL/TLS tự động)
    redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5
    )
    redis_client.ping()
    app_logger.info("Đã kết nối Upstash Redis thành công!")
except Exception as e:
    app_logger.error(f"Kết nối Upstash thất bại: {e}")
    redis_client = None


# ── Fallback in-process cache khi Redis không có ──────────────────────────────
_local_cache: dict = {}
_LOCAL_CACHE_MAX = 500


def _generate_key(query: str, scope: str, is_first_message: bool = True) -> str:
    """
    Tạo cache key từ query + scope + is_first_message.
    is_first_message ảnh hưởng lời chào nên cần phân biệt.
    """
    raw_str = f"{scope}_{int(is_first_message)}_{query.lower().strip()}"
    hash_str = hashlib.md5(raw_str.encode("utf-8")).hexdigest()
    return f"chat_cache:{hash_str}"


def get_cached_answer(query: str, scope: str, is_first_message: bool = True):
    """Lấy câu trả lời từ cache (Redis ưu tiên, fallback in-process)."""
    key = _generate_key(query, scope, is_first_message)

    if redis_client:
        try:
            data = redis_client.get(key)
            if data:
                app_logger.debug("Redis cache HIT")
                return json.loads(data)
            return None
        except Exception as e:
            app_logger.error(f"Lỗi khi đọc Redis Cache: {e}")

    # Fallback: in-process dict
    return _local_cache.get(key)


def set_cached_answer(query: str, scope: str, is_first_message: bool, result_data: dict):
    """Lưu câu trả lời vào cache (Redis ưu tiên, fallback in-process)."""
    # Tránh cache câu trả lời trống hoặc câu trả lời lỗi kết nối AI
    if not result_data:
        return

    answer = result_data.get("answer", "")
    if is_error_response(answer):
        app_logger.warning(f"⚠️ Phát hiện câu trả lời lỗi/hệ thống hoặc trống: '{answer[:60]}...'. Bỏ qua không lưu cache.")
        return

    key = _generate_key(query, scope, is_first_message)

    if redis_client:
        try:
            redis_client.set(key, json.dumps(result_data), ex=settings.CACHE_TTL)
            return
        except Exception as e:
            app_logger.error(f"Lỗi khi ghi Redis Cache: {e}")

    # Fallback: in-process dict (giới hạn kích thước)
    if len(_local_cache) >= _LOCAL_CACHE_MAX:
        # Xoá 100 entry đầu
        for k in list(_local_cache.keys())[:100]:
            del _local_cache[k]
    _local_cache[key] = result_data

