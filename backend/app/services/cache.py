import redis
import hashlib
import json
from app.config import settings
from app.utils.logger import app_logger

# Khởi tạo kết nối Redis
try:
    # decode_responses=True giúp dữ liệu lấy ra là String thay vì Bytes
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()  # Gửi request test xem Redis có sống không
    app_logger.info("✅ Đã kết nối thành công với Redis Local!")
except Exception as e:
    app_logger.error(f"⚠️ Không thể kết nối Redis. Hệ thống sẽ bỏ qua Cache. Lỗi: {e}")
    redis_client = None

def _generate_key(query: str, scope: str) -> str:
    # Cộng thêm scope vào chuỗi hash
    raw_str = f"{scope}_{query.lower().strip()}"
    hash_str = hashlib.md5(raw_str.encode('utf-8')).hexdigest()
    return f"chat_cache:{hash_str}"


def get_cached_answer(query: str, scope: str):
    """Lấy câu trả lời từ Redis Cache"""
    if not redis_client:
        return None
        
    try:
        key = _generate_key(query, scope)
        data = redis_client.get(key)
        if data:
            return json.loads(data) # Ép ngược lại thành Dictionary
        return None
    except Exception as e:
        app_logger.error(f"Lỗi khi đọc Redis Cache: {e}")
        return None
        

def set_cached_answer(query: str, scope: str, result_data: dict):
    """Lưu câu trả lời vào Redis với thời gian hết hạn (TTL)"""
    if not redis_client:
        return
        
    try:
        key = _generate_key(query, scope)
        # Lưu vào Redis kèm theo thời gian sống (ex = expires in seconds)
        redis_client.set(key, json.dumps(result_data), ex=settings.CACHE_TTL)
    except Exception as e:
        app_logger.error(f"Lỗi khi ghi Redis Cache: {e}")