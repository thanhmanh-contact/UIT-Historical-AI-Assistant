"""
API endpoints quản lý phiên chat.

Frontend gọi DELETE khi user bấm "Cuộc trò chuyện mới".
GET dùng để debug / kiểm tra history (tuỳ chọn).
"""
from fastapi import APIRouter, HTTPException
from app.services import session as session_svc
from app.utils.logger import app_logger

router = APIRouter()


@router.delete("/session/{session_id}")
async def clear_chat_session(session_id: str):
    """
    Xoá lịch sử của một phiên chat (New Chat).
    Frontend tự sinh session_id mới sau khi gọi endpoint này.
    """
    if not session_id or len(session_id) < 8:
        raise HTTPException(status_code=400, detail="session_id không hợp lệ.")
    try:
        session_svc.clear_session(session_id)
        return {"status": "success", "message": "Đã xoá lịch sử phiên chat."}
    except Exception as e:
        app_logger.error(f"❌ Lỗi xoá session: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống.")


@router.get("/session/{session_id}")
async def get_session_history(session_id: str):
    """Lấy lịch sử hội thoại của phiên (dùng để debug)."""
    history = session_svc.get_history(session_id)
    return {
        "session_id": session_id,
        "turn_count": len(history),
        "history": history
    }
