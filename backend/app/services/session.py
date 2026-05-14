"""
Quản lý phiên hội thoại (Session Management).

Mỗi phiên chat có một session_id duy nhất.
Lịch sử hội thoại được lưu vào Redis với TTL 7 ngày.
Nếu Redis không khả dụng, fallback sang in-memory dict (mất khi restart server).
"""
import json
import uuid
from app.services.cache import redis_client
from app.utils.logger import app_logger
from app.config import settings

SESSION_TTL = 60 * 60 * 24 * 7  # 7 ngày (giây)

# Fallback in-memory nếu Redis offline
_mem_store: dict[str, list] = {}


def _key(session_id: str) -> str:
    return f"session:{session_id}"


def new_session_id() -> str:
    """Tạo một session_id mới (UUID4). Không cần gọi backend."""
    return str(uuid.uuid4())


def get_history(session_id: str) -> list[dict]:
    """
    Lấy toàn bộ lịch sử hội thoại của phiên.
    Trả về list các dict: [{question, answer, scope}, ...]
    """
    try:
        if redis_client:
            raw = redis_client.get(_key(session_id))
            return json.loads(raw) if raw else []
        return _mem_store.get(session_id, [])
    except Exception as e:
        app_logger.error(f"❌ get_history({session_id}): {e}")
        return []


def append_turn(session_id: str, question: str, answer: str, scope: str) -> None:
    """Thêm một lượt Q&A vào lịch sử phiên."""
    history = get_history(session_id)
    history.append({"question": question, "answer": answer, "scope": scope})

    # Giới hạn kích thước để tránh prompt quá dài
    max_turns = settings.MAX_HISTORY_TURNS * 2
    if len(history) > max_turns:
        history = history[-max_turns:]

    _save(session_id, history)


def clear_session(session_id: str) -> None:
    """Xoá toàn bộ lịch sử của phiên (dùng khi bấm 'Cuộc trò chuyện mới')."""
    _save(session_id, [])
    app_logger.info(f"🗑 Đã xoá lịch sử phiên {session_id[:8]}…")


def _save(session_id: str, history: list) -> None:
    try:
        if redis_client:
            redis_client.set(
                _key(session_id),
                json.dumps(history, ensure_ascii=False),
                ex=SESSION_TTL
            )
        else:
            _mem_store[session_id] = history
    except Exception as e:
        app_logger.error(f"❌ _save({session_id}): {e}")
