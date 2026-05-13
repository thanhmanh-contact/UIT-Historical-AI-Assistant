from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid

from app.services.rag import generate_answer
from app.utils.sanitize import clean_and_validate_input
from app.utils.logger import app_logger

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    scope: Optional[str] = "auto"
    is_first_message: bool = True

class ChatResponse(BaseModel):
    message_id: str
    answer: str
    sources: List[dict]
    suggestions: List[str]
    detected_scope: str 

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    # 1. Ghi log có user request
    app_logger.info(f"User Request: {request.message} | Scope: {request.scope}")
    
    try:
        # 2. Làm sạch đầu vào 
        safe_message = clean_and_validate_input(request.message)
        
        # 3. Gọi hàm RAG (CHỈ GỌI 1 LẦN DUY NHẤT Ở ĐÂY)
        rag_result = generate_answer(safe_message, request.scope, request.is_first_message)
        scope_result = rag_result["scope"]
        
        # 4. Lấy suggestions từ AI (fallback nếu cache cũ không có)
        suggestions = rag_result.get(
            "suggestions",
            ["Kể về lịch sử hình thành?", "Những thành tựu nổi bật?", "Đời sống sinh viên ra sao?"]
        )

        # 5. Ghi log thành công
        answer_text = rag_result["answer"]
        app_logger.info(f"AI Response: {answer_text[:50]}...") 
        
        # 6. Trả về kết quả cho Frontend
        msg_id = str(uuid.uuid4())
        
        return ChatResponse(
            message_id=msg_id,
            answer=answer_text,
            sources=rag_result["sources"],
            suggestions=suggestions,
            detected_scope=scope_result
        )          
        
    except HTTPException as he:
        app_logger.warning(f"Validation Error: {he.detail}")
        raise he
    except Exception as e:
        app_logger.error(f"Internal System Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Hệ thống đang bận, vui lòng thử lại sau.")