import re
from fastapi import HTTPException
from app.config import settings

def clean_and_validate_input(text: str) -> str:
    """
    Làm sạch văn bản đầu vào và kiểm tra tính hợp lệ.
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống.")

    # 1. Loại bỏ các thẻ HTML (nếu user cố tình chèn <script>...)
    clean_text = re.sub(r'<[^>]+>', '', text)
    
    # 2. Xóa các ký tự đặc biệt không cần thiết (chỉ giữ lại chữ, số và dấu câu cơ bản)
    # clean_text = re.sub(r'[^\w\s\.,\?!]', '', clean_text) 
    
    # 3. Chuẩn hóa khoảng trắng (xóa khoảng trắng thừa)
    clean_text = " ".join(clean_text.split())
    
    # 4. Kiểm tra độ dài (Bảo vệ hầu bao của bạn khỏi việc spam token)
    if len(clean_text) > settings.MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Câu hỏi quá dài. Vui lòng tóm tắt dưới {settings.MAX_INPUT_LENGTH} ký tự."
        )
        
    return clean_text


def is_error_response(answer: str) -> bool:
    """
    Kiểm tra câu trả lời có phải là lỗi hệ thống hoặc fallback hay không.
    Nếu đúng, trả về True để tránh lưu vào Cache hoặc Session History.
    """
    if not answer or not answer.strip():
        return True

    # Chuẩn hóa về chữ thường và loại bỏ dấu tiếng Việt để so khớp dễ dàng
    def clean_text(t: str) -> str:
        t = t.lower()
        import unicodedata
        try:
            t = unicodedata.normalize('NFD', t)
            t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
            t = t.replace('đ', 'd').replace('Đ', 'd')
        except Exception:
            pass
        return t

    answer_clean = clean_text(answer)

    error_patterns = [
        "su co ket noi",
        "co loi xay ra",
        "tam thoi khong kha dung",
        "he thong dang ban",
        "gap su co",
        "rat tiec",
        "thu lai sau",
        "khong kha dung",
        "thu lai nhe",
        "vui long thu lai",
        "he thong gap su co",
        "dich vu ai tam thoi",
        "connection error",
        "system error",
        "rate limit",
        "qua nhieu yeu cau",
        # Các mẫu phản hồi khi không tìm thấy dữ liệu/thông tin
        "chua cap nhat thong tin",
        "khong co thong tin",
        "khong tim thay thong tin",
        "du lieu chua co",
        "nam ngoai pham vi du lieu",
        "khong du du lieu",
        "khong co trong tai lieu",
        "tai lieu khong de cap",
        "hien tai minh khong co",
        "khong tim thay du lieu",
        "minh khong tim thay",
    ]

    return any(pattern in answer_clean for pattern in error_patterns)