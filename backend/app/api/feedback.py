from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import json
import os
import threading
_file_lock = threading.Lock()
from app.utils.logger import app_logger

router = APIRouter()

LOG_DIR = "data/feedback"
ALLOWED_FEEDBACK_TYPES = {"like", "dislike"}


class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str
    user_note: Optional[str] = ""
    question: Optional[str] = ""
    answer: Optional[str] = ""

    @field_validator("feedback_type")
    @classmethod
    def validate_feedback_type(cls, v):
        """BUG FIX: Validate feedback_type hợp lệ — trước đây bất kỳ string nào đều được chấp nhận."""
        if v not in ALLOWED_FEEDBACK_TYPES:
            raise ValueError(f"feedback_type phải là 'like' hoặc 'dislike', nhận được: '{v}'")
        return v

    @field_validator("message_id")
    @classmethod
    def validate_message_id(cls, v):
        """Kiểm tra message_id không trống."""
        if not v or not v.strip():
            raise ValueError("message_id không được để trống.")
        return v.strip()


def _atomic_append_feedback(file_path: str, new_entry: dict) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with _file_lock:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []
        logs.append(new_entry)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)


@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    try:
        feedback_data = {
            "message_id": req.message_id,
            "timestamp": datetime.now().isoformat(),
            "question": req.question,
            "answer": req.answer,
        }

        if req.feedback_type == "dislike":
            feedback_data["user_note"] = req.user_note

        file_name = "likes.json" if req.feedback_type == "like" else "dislikes.json"
        file_path = os.path.join(LOG_DIR, file_name)

        _atomic_append_feedback(file_path, feedback_data)

        app_logger.info(f"✅ Feedback '{req.feedback_type}' cho message {req.message_id}")
        return {"status": "success", "feedback_type": req.feedback_type}

    except Exception as e:
        app_logger.error(f"❌ Lỗi lưu feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi lưu feedback.")


@router.get("/feedback/stats")
async def get_feedback_stats():
    """
    IMPROVEMENT: Endpoint thống kê feedback để theo dõi chất lượng chatbot.
    Trả về số lượng like/dislike và danh sách câu hỏi bị dislike gần nhất.
    """
    stats = {"likes": 0, "dislikes": 0, "recent_dislikes": []}
    try:
        likes_path = os.path.join(LOG_DIR, "likes.json")
        dislikes_path = os.path.join(LOG_DIR, "dislikes.json")

        if os.path.exists(likes_path):
            with open(likes_path, "r", encoding="utf-8") as f:
                likes_data = json.load(f)
                stats["likes"] = len(likes_data)

        if os.path.exists(dislikes_path):
            with open(dislikes_path, "r", encoding="utf-8") as f:
                dislikes_data = json.load(f)
                stats["dislikes"] = len(dislikes_data)
                # Trả về 10 dislike gần nhất để review
                stats["recent_dislikes"] = [
                    {
                        "timestamp": d.get("timestamp"),
                        "question": d.get("question", "")[:100],
                        "user_note": d.get("user_note", ""),
                    }
                    for d in dislikes_data[-10:]
                ]

        total = stats["likes"] + stats["dislikes"]
        stats["satisfaction_rate"] = (
            round(stats["likes"] / total * 100, 1) if total > 0 else None
        )
        return stats

    except Exception as e:
        app_logger.error(f"❌ Lỗi đọc feedback stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Lỗi khi đọc thống kê feedback.")
