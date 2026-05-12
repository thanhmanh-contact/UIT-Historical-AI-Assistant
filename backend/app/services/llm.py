from google import genai
from google.genai import types
from app.config import settings

# Khởi tạo Client theo chuẩn mới
client = genai.Client(
                        api_key=settings.GOOGLE_API_KEY,
                        http_options=types.HttpOptions(api_version="v1beta")
)

def generate_text(query: str, context: str, scope: str) -> str:
    # Xác định vai trò
    role_name = "Trường Đại học Công nghệ Thông tin (UIT)" if scope == "uit" else "Khoa Công nghệ Phần mềm (CNPM) - Trường UIT"
    
    # Hướng dẫn cho AI
    sys_instruct = f"""Bạn là chuyên gia tư vấn và trợ lý AI ảo đại diện cho {role_name}.
Nhiệm vụ của bạn là cung cấp thông tin CHÍNH XÁC, ĐẦY ĐỦ và CHI TIẾT.

QUY TẮC NGHIÊM NGẶT:
1. Tuyệt đối bám sát tài liệu được cung cấp. Hãy tổng hợp và liệt kê rõ ràng các năm tháng, sự kiện, thành tựu.
2. CẤM trả lời chung chung qua loa. Nếu tài liệu có nhiều ý, hãy trình bày bằng gạch đầu dòng (-) cho dễ đọc.
3. Nếu tài liệu hoàn toàn KHÔNG chứa thông tin liên quan, hãy từ chối khéo: "Dạ, hiện tại dữ liệu của em chưa cập nhật thông tin chi tiết về vấn đề này."
4. Luôn giữ thái độ thân thiện, xưng "em/mình" và gọi người dùng là "bạn", thỉnh thoảng sử dụng emoji ✨."""

    prompt = f"""TÀI LIỆU CUNG CẤP:
{context}

CÂU HỎI TỪ NGƯỜI DÙNG:
{query}"""

    try:
        # Gọi API với model name đã được làm sạch
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct,
                temperature=settings.TEMPERATURE,
                max_output_tokens=settings.MAX_TOKENS,
            )
        )
        return response.text
    except Exception as e:
        # Ghi log lỗi chi tiết để debug
        print(f"❌ Lỗi LLM: {e}")
        return "Dạ, mình đang gặp chút sự cố kết nối với bộ não AI. Bạn thử lại sau giây lát nhé!"