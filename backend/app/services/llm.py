import json
from google import genai
from google.genai import types
from app.config import settings
from app.utils.logger import app_logger
from typing import Optional

client = genai.Client(
    api_key=settings.GOOGLE_API_KEY,
    http_options=types.HttpOptions(api_version="v1beta")
)

_FALLBACK = {
    "answer": "Dạ, mình đang gặp chút sự cố kết nối với bộ não AI. Bạn thử lại sau giây lát nhé! 🙏",
    "suggestions": ["Kể về lịch sử hình thành?", "Những thành tựu nổi bật?", "Đời sống sinh viên ra sao?"],
}


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
    conversation_history: Optional[list] = None
) -> dict:
    """
    Sinh câu trả lời từ Gemini LLM với hỗ trợ hội thoại nhiều lượt.
    Xưng hô: "mình" (đã sửa từ "em/mình").
    """
    role_name = (
        "Trường Đại học Công nghệ Thông tin (UIT)"
        if scope == "uit"
        else "Khoa Công nghệ Phần mềm (CNPM) - Trường UIT"
    )

    history_block = _build_history_block(conversation_history or [])

    sys_instruct = f"""Bạn là chuyên gia tư vấn và trợ lý AI ảo đại diện cho {role_name}.
Nhiệm vụ của bạn là cung cấp thông tin CHÍNH XÁC, ĐẦY ĐỦ và CHI TIẾT.

QUY TẮC NGHIÊM NGẶT:
1. Tuyệt đối bám sát tài liệu được cung cấp. Hãy tổng hợp và liệt kê rõ ràng các năm tháng, sự kiện, thành tựu.
2. CẤM trả lời chung chung qua loa. Nếu tài liệu có nhiều ý, hãy trình bày bằng gạch đầu dòng (-) cho dễ đọc.
3. Nếu tài liệu hoàn toàn KHÔNG chứa thông tin liên quan, hãy từ chối khéo: "Dạ, hiện tại dữ liệu của mình chưa cập nhật thông tin chi tiết về vấn đề này."
4. Luôn giữ thái độ thân thiện, xưng "mình" và gọi người dùng là "bạn", thỉnh thoảng sử dụng emoji ✨.
5. {"Chào người dùng tự nhiên ở đầu câu trả lời." if is_first_message else "KHÔNG chào hỏi (Xin chào, Dạ chào,...), đi thẳng vào nội dung."}
6. Nếu có LỊCH SỬ HỘI THOẠI, hãy tham chiếu ngữ cảnh đó để câu trả lời liền mạch, tự nhiên.

ĐỊNH DẠNG ĐẦU RA (JSON):
Trả về đúng JSON sau, không thêm bất kỳ text nào ngoài JSON:
{{
  "answer": "<câu trả lời chi tiết ở đây>",
  "suggestions": ["<gợi ý 1>", "<gợi ý 2>", "<gợi ý 3>"]
}}

QUY TẮC CHO SUGGESTIONS:
- Đúng 3 gợi ý, mỗi gợi ý tối đa 8 từ tiếng Việt
- Tiếp nối câu chuyện tự nhiên từ câu trả lời vừa rồi (như "chương tiếp theo")
- Không lặp lại nội dung câu hỏi hiện tại
- Dẫn dắt người dùng khám phá sâu hơn về {role_name}"""

    prompt_parts = []
    if history_block:
        prompt_parts.append(history_block)
    prompt_parts.append(f"TÀI LIỆU CUNG CẤP:\n{context}")
    prompt_parts.append(f"CÂU HỎI TỪ NGƯỜI DÙNG:\n{query}")
    prompt = "\n\n".join(prompt_parts)

    try:
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                temperature=settings.TEMPERATURE,
                max_output_tokens=settings.MAX_TOKENS,
                response_mime_type="application/json",
            )
        )
        data = json.loads(response.text)
        return {
            "answer": str(data.get("answer", _FALLBACK["answer"])),
            "suggestions": list(data.get("suggestions", _FALLBACK["suggestions"]))[:3],
        }
    except Exception as e:
        app_logger.error(f"❌ Lỗi LLM: {e}", exc_info=True)
        return _FALLBACK
