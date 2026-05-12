from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional 
from datetime import datetime
import json
import os
from app.utils.logger import app_logger

router = APIRouter()

# 1. THÊM 2 TRƯỜNG QUESTION VÀ ANSWER VÀO ĐÂY
class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str 
    user_note: Optional[str] = "" 
    question: Optional[str] = ""  
    answer: Optional[str] = ""  

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    try:
        # 2. ĐƯA DATA VÀO ĐỂ LƯU
        feedback_data = {
            "message_id": req.message_id,
            "timestamp": datetime.now().isoformat(),
            "question": req.question,  # Lưu câu hỏi
            "answer": req.answer       # Lưu câu trả lời
        }
        
        log_dir = "data/feedback"
        os.makedirs(log_dir, exist_ok=True)
        
        if req.feedback_type == "like":
            file_path = os.path.join(log_dir, "likes.json")
        else:
            file_path = os.path.join(log_dir, "dislikes.json")
            feedback_data["user_note"] = req.user_note 
            
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        else:
            logs =[]
            
        logs.append(feedback_data)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
            
        app_logger.info(f"Đã nhận feedback '{req.feedback_type}' cho tin nhắn {req.message_id}")
        return {"status": "success"}
        
    except Exception as e:
        app_logger.error(f"Lỗi lưu feedback: {e}")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống")