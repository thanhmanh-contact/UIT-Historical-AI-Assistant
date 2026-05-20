"""
llm.py — Gemini LLM Service (v2.5)

Tính năng:
  - Hỗ trợ hội thoại đa lượt (Conversation History).
  - Tự động fallback sang Server Key nếu User Key bị lỗi.
  - Prompt chuyên nghiệp đại diện cho UIT.
"""

import json
from app.config import settings
from app.utils.logger import app_logger
from typing import Optional

_FALLBACK = {
    "answer": "Dạ, mình đang gặp chút sự cố kết nối AI. Bạn thử lại sau nhé!",
    "suggestions": ["Lịch sử UIT?", "Thành tựu UIT?", "Đời sống sinh viên?"],
}

def _get_client(api_key: str = ""):
    """Khởi tạo Gemini client với key tùy chọn."""
    key = api_key or settings.GOOGLE_API_KEY
    if not key:
        raise RuntimeError("Không có API Key nào khả dụng.")
    
    from google import genai
    from google.genai import types
    return genai.Client(
        api_key=key,
        http_options=types.HttpOptions(api_version="v1beta"),
    )

def _build_history_block(conversation_history: list) -> str:
    """Chuyển lịch sử hội thoại thành chuỗi văn bản cho LLM."""
    if not conversation_history:
        return ""
    lines = ["LỊCH SỬ HỘI THOẠI TRƯỚC ĐÓ:"]
    for turn in conversation_history[-settings.MAX_HISTORY_TURNS:]:
        lines.append(f"Người dùng: {turn.get('question', '')}")
        lines.append(f"Trợ lý: {turn.get('answer', '')}")
    return "\n".join(lines)

def generate_text(
    query: str,
    context: str,
    scope: str,
    is_first_message: bool = True,
    conversation_history: Optional[list] = None,
    used_web: bool = False,
    api_key: str = "",
) -> dict:
    """Sinh câu trả lời với đầy đủ ngữ cảnh và cơ chế fallback key."""
    from google.genai import types

    role_name = "Trường Đại học Công nghệ Thông tin (UIT)" if scope == "uit" else "Khoa Công nghệ Phần mềm (CNPM) - Trường UIT"
    history_block = _build_history_block(conversation_history or [])
    context_note = "Nguồn: Website UIT (Real-time)." if used_web else "Nguồn: Dữ liệu nội bộ UIT."

    sys_instruct = f"""Bạn là trợ lý AI chuyên nghiệp của {role_name}.
Nhiệm vụ: Trả lời CHI TIẾT và CHÍNH XÁC dựa trên tài liệu.
Quy tắc:
1. Nếu không có thông tin, trả lời đúng: "Dạ, hiện tại dữ liệu của mình chưa cập nhật thông tin chi tiết về vấn đề này."
2. Luôn xưng "mình" và gọi "bạn", trả lời thân thiện và tự nhiên.
3. {"Chào bạn!" if is_first_message else "Đi thẳng vào nội dung, không chào lại."}
Định dạng JSON: {{"answer": "...", "suggestions": ["...", "...", "..."]}}"""

    prompt = f"{history_block}\n\n{context_note}\nTÀI LIỆU:\n{context}\n\nCÂU HỎI:\n{query}"

    def _call_gemini(target_key):
        client = _get_client(target_key)
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                temperature=settings.TEMPERATURE,
                max_output_tokens=settings.MAX_TOKENS,
                response_mime_type="application/json",
            ),
        )
        # Xử lý bóc tách JSON
        raw = response.text.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        return json.loads(raw)

    try:
        # Thử với Key được yêu cầu (User hoặc Server)
        target_key = api_key or settings.GOOGLE_API_KEY
        key_type = "User Key" if api_key else "Server Key"
        app_logger.info(f"Đang gọi LLM bằng {key_type} (đuôi: ...{target_key[-4:]})")
        
        data = _call_gemini(api_key)
        return {
            "answer": str(data.get("answer", _FALLBACK["answer"])),
            "suggestions": list(data.get("suggestions", _FALLBACK["suggestions"]))[:3],
        }
    except Exception as e:
        # Fallback sang Server Key nếu lỗi và đang dùng User Key
        if api_key and api_key != settings.GOOGLE_API_KEY:
            app_logger.warning(f"User API Key lỗi, thử lại bằng Server Key... {e}")
            try:
                data = _call_gemini(settings.GOOGLE_API_KEY)
                return {
                    "answer": str(data.get("answer", _FALLBACK["answer"])),
                    "suggestions": list(data.get("suggestions", _FALLBACK["suggestions"]))[:3],
                }
            except Exception as e2:
                app_logger.error(f"Cả 2 Key đều lỗi LLM: {e2}")
        
        app_logger.error(f"Lỗi LLM: {e}")
        return _FALLBACK
