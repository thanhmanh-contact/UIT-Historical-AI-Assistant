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