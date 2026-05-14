from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict
import uuid
import time
from collections import defaultdict

from app.services.rag import generate_answer
from app.services import session as session_svc
from app.utils.sanitize import clean_and_validate_input
from app.utils.logger import app_logger
from app.config import settings

router = APIRouter()

# ── Rate Limiting (in-memory theo IP) ─────────────────────────────────────────
_rate_store: Dict[str, list] = defaultdict(list)

def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    window = settings.RATE_LIMIT_WINDOW_SECONDS
    _rate_store[ip] = [t for t in _rate_store[ip] if now - t < window]
    if len(_rate_store[ip]) >= settings.RATE_LIMIT_MAX_REQUESTS:
        return False
    _rate_store[ip].append(now)
    return True


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    scope: Optional[str] = "auto"
    is_first_message: bool = True
    session_id: Optional[str] = None   # None = không dùng session

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v):
        if v not in {"auto", "uit", "cnpm"}:
            raise ValueError("scope phải là một trong: auto, uit, cnpm")
        return v


class ChatResponse(BaseModel):
    message_id: str
    answer: str
    sources: List[dict]
    suggestions: List[str]
    detected_scope: str


# ── Endpoint /chat ─────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, http_request: Request):
    # 1. Rate limiting theo IP
    client_ip = getattr(http_request.client, "host", "unknown")
    if not _check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Bạn đang gửi quá nhiều yêu cầu. Thử lại sau {settings.RATE_LIMIT_WINDOW_SECONDS} giây."
        )

    app_logger.info(
        f"Chat | scope={request.scope} | "
        f"session={str(request.session_id)[:8] if request.session_id else 'none'} | "
        f"msg={request.message[:60]}"
    )

    try:
        # 2. Làm sạch đầu vào
        safe_msg = clean_and_validate_input(request.message)

        # 3. Tải lịch sử hội thoại từ session
        history = None
        if request.session_id:
            raw = session_svc.get_history(request.session_id)
            if raw:
                history = raw  # list[{question, answer, scope}]

        # 4. Gọi RAG pipeline
        rag_result = generate_answer(
            query=safe_msg,
            current_scope=request.scope,
            is_first_message=request.is_first_message,
            conversation_history=history
        )

        answer_text  = rag_result["answer"]
        scope_result = rag_result["scope"]
        suggestions  = rag_result.get(
            "suggestions",
            ["Kể về lịch sử hình thành?", "Những thành tựu nổi bật?", "Đời sống sinh viên ra sao?"]
        )

        # 5. Lưu lượt hội thoại vào session
        if request.session_id:
            session_svc.append_turn(
                session_id=request.session_id,
                question=safe_msg,
                answer=answer_text,
                scope=scope_result
            )

        app_logger.info(f"Trả lời (scope={scope_result}): {answer_text[:80]}…")

        return ChatResponse(
            message_id=str(uuid.uuid4()),
            answer=answer_text,
            sources=rag_result["sources"],
            suggestions=suggestions,
            detected_scope=scope_result
        )

    except HTTPException as he:
        app_logger.warning(f"HTTP Error: {he.detail}")
        raise
    except RuntimeError as re:
        app_logger.error(f"Service Error: {re}")
        raise HTTPException(status_code=503, detail="Dịch vụ AI tạm thời không khả dụng. Vui lòng thử lại.")
    except Exception as e:
        app_logger.error(f"Internal Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Hệ thống đang bận, vui lòng thử lại sau.")
