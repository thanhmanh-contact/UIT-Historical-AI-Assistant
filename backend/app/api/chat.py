from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional, Dict
import uuid
import asyncio
import json
import time
from collections import defaultdict

from app.services.rag import generate_answer, detect_scope, _is_realtime_query
from app.services import session as session_svc
from app.utils.sanitize import clean_and_validate_input
from app.utils.logger import app_logger
from app.config import settings

router = APIRouter()

# ── Rate Limiting ─────────────────────────────────────────────────────────────
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
    session_id: Optional[str] = None

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, v):
        if v not in {"auto", "uit", "cnpm"}:
            raise ValueError("scope phai la mot trong: auto, uit, cnpm")
        return v


class ChatResponse(BaseModel):
    message_id: str
    answer: str
    sources: List[dict]
    suggestions: List[str]
    detected_scope: str


# ── Thinking stage helpers ─────────────────────────────────────────────────────

def _thinking_message(stage: str, query: str) -> str:
    lower = query.lower()
    if stage == "analyzing":
        if any(w in lower for w in ["tai sao", "vi sao", "ly do", "tại sao", "vì sao"]):
            return "Đang phân tích câu hỏi..."
        if any(w in lower for w in ["so sanh", "khac nhau", "giong", "so sánh", "khác nhau"]):
            return "Đang xác định trọng tâm câu hỏi..."
        return "Đang đọc và phân tích yêu cầu..."
    if stage == "searching":
        if any(w in lower for w in ["lich su", "thanh lap", "ra doi", "lịch sử", "thành lập", "ra đời"]):
            return "Đang tra cứu lịch sử..."
        if any(w in lower for w in ["thanh tuu", "giai thuong", "thanh ich", "thành tựu", "giải thưởng"]):
            return "Đang tìm kiếm thành tựu và dấu ấn..."
        if any(w in lower for w in ["sinh vien", "hoc phi", "ky tuc", "sinh viên", "học phí"]):
            return "Đang tìm thông tin sinh viên..."
        if any(w in lower for w in ["nganh", "chuong trinh", "dao tao", "ngành", "đào tạo"]):
            return "Đang tra cứu chương trình đào tạo..."
        if any(w in lower for w in ["giang vien", "giao vien", "tien si", "giảng viên", "tiến sĩ"]):
            return "Đang tìm thông tin giảng viên..."
        if any(w in lower for w in ["doanh nghiep", "doi tac", "hop tac", "doanh nghiệp", "đối tác"]):
            return "Đang tra cứu đối tác doanh nghiệp..."
        return "Đang tìm kiếm trong cơ sở dữ liệu..."
    if stage == "web_searching":
        return "Đang tìm kiếm thông tin trực tuyến..."
    if stage == "found":
        return "Đã tìm thấy thông tin liên quan"
    if stage == "generating":
        if any(w in lower for w in ["ke", "cau chuyen", "hanh trinh", "kể", "câu chuyện", "hành trình"]):
            return "Đang soạn câu chuyện..."
        if any(w in lower for w in ["giai thich", "tai sao", "vi sao", "giải thích", "tại sao"]):
            return "Đang soạn giải thích..."
        return "Đang soạn câu trả lời..."
    return "Đang xử lý..."


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# ── Endpoint /chat (giữ nguyên) ────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest, http_request: Request):
    client_ip = getattr(http_request.client, "host", "unknown")
    if not _check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Ban dang gui qua nhieu yeu cau. Thu lai sau {settings.RATE_LIMIT_WINDOW_SECONDS} giay."
        )

    app_logger.info(
        f"Chat | scope={request.scope} | "
        f"session={str(request.session_id)[:8] if request.session_id else 'none'} | "
        f"msg={request.message[:60]}"
    )

    api_key = http_request.headers.get("X-API-Key", "").strip() or settings.GOOGLE_API_KEY
    if not api_key:
        raise HTTPException(status_code=401, detail="Vui long cung cap Google API key.")

    try:
        safe_msg = clean_and_validate_input(request.message)

        history = None
        if request.session_id:
            raw = session_svc.get_history(request.session_id)
            if raw:
                history = raw

        rag_result = generate_answer(
            query=safe_msg,
            current_scope=request.scope,
            is_first_message=request.is_first_message,
            conversation_history=history,
            api_key=api_key,
        )

        answer_text  = rag_result["answer"]
        scope_result = rag_result["scope"]
        suggestions  = rag_result.get("suggestions", [])

        if request.session_id:
            session_svc.append_turn(
                session_id=request.session_id,
                question=safe_msg,
                answer=answer_text,
                scope=scope_result
            )

        app_logger.info(f"Tra loi (scope={scope_result}): {answer_text[:80]}...")

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
        raise HTTPException(status_code=503, detail="Dich vu AI tam thoi khong kha dung.")
    except Exception as e:
        app_logger.error(f"Internal Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="He thong dang ban, vui long thu lai sau.")


# ── Endpoint /chat/stream (SSE) ────────────────────────────────────────────────

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, http_request: Request):
    """SSE endpoint phat tung buoc: thinking -> token -> done"""
    client_ip = getattr(http_request.client, "host", "unknown")
    if not _check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Ban dang gui qua nhieu yeu cau. Thu lai sau {settings.RATE_LIMIT_WINDOW_SECONDS} giay."
        )

    api_key = http_request.headers.get("X-API-Key", "").strip() or settings.GOOGLE_API_KEY
    if not api_key:
        raise HTTPException(status_code=401, detail="Vui long cung cap Google API key.")

    async def event_generator():
        try:
            safe_msg = clean_and_validate_input(request.message)

            # Stage 1: Phan tich
            yield _sse({"type": "thinking", "stage": "analyzing",
                        "message": _thinking_message("analyzing", safe_msg)})
            await asyncio.sleep(0.35)

            # Stage 2: Tim kiem
            yield _sse({"type": "thinking", "stage": "searching",
                        "message": _thinking_message("searching", safe_msg)})
            await asyncio.sleep(0.25)

            # Stage 3: Web search neu realtime
            if _is_realtime_query(safe_msg):
                yield _sse({"type": "thinking", "stage": "web_searching",
                            "message": _thinking_message("web_searching", safe_msg)})
                await asyncio.sleep(0.2)

            # Lich su session
            history = None
            if request.session_id:
                raw = session_svc.get_history(request.session_id)
                if raw:
                    history = raw

            # Chay RAG pipeline trong thread
            loop = asyncio.get_event_loop()
            rag_result = await loop.run_in_executor(
                None,
                lambda: generate_answer(
                    query=safe_msg,
                    current_scope=request.scope,
                    is_first_message=request.is_first_message,
                    conversation_history=history,
                    api_key=api_key,
                )
            )

            answer_text  = rag_result["answer"]
            scope_result = rag_result["scope"]
            suggestions  = rag_result.get("suggestions", [])

            # Stage 4: Da tim thay
            yield _sse({"type": "thinking", "stage": "found",
                        "message": _thinking_message("found", safe_msg)})
            await asyncio.sleep(0.18)

            # Stage 5: Dang soan
            yield _sse({"type": "thinking", "stage": "generating",
                        "message": _thinking_message("generating", safe_msg)})
            await asyncio.sleep(0.28)

            # Stream tung cum ky tu (4 chars / 12ms ≈ 333 chars/s)
            chunk_size = 4
            for i in range(0, len(answer_text), chunk_size):
                yield _sse({"type": "token", "text": answer_text[i:i + chunk_size]})
                await asyncio.sleep(0.012)

            # Luu session
            if request.session_id:
                session_svc.append_turn(
                    session_id=request.session_id,
                    question=safe_msg,
                    answer=answer_text,
                    scope=scope_result
                )

            message_id = str(uuid.uuid4())
            app_logger.info(f"[stream] Done scope={scope_result} len={len(answer_text)}")
            yield _sse({
                "type": "done",
                "message_id": message_id,
                "sources": rag_result["sources"],
                "suggestions": suggestions,
                "detected_scope": scope_result,
            })

        except Exception as e:
            app_logger.error(f"[stream] Loi: {e}", exc_info=True)
            yield _sse({"type": "error", "message": "He thong gap su co, vui long thu lai."})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
