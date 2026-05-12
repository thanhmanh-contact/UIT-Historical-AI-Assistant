from google import genai
import os
from dotenv import load_dotenv

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# 2. Khởi tạo Client (Thử nghiệm trên cả v1 và v1beta nếu cần)
client = genai.Client(api_key=api_key)

print("="*50)
print("🔍 ĐANG QUÉT TẤT CẢ MODEL TƯƠNG THÍCH VỚI KEY CỦA BẠN")
print("="*50)

try:
    models = list(client.models.list())
    
    print("\n[1] --- CÁC MODEL DÙNG ĐỂ CHAT / SINH VĂN BẢN (LLM_MODEL) ---")
    for m in models:
        if 'generateContent' in m.supported_actions:
            print(f"ID: {m.name} | Tên: {m.display_name}")

    print("\n[2] --- CÁC MODEL DÙNG ĐỂ NHÚNG VECTOR (EMBEDDING_MODEL) ---")
    for m in models:
        if 'embedContent' in m.supported_actions:
            print(f"ID: {m.name} | Tên: {m.display_name}")

    print("\n" + "="*50)
    print("💡 LƯU Ý: Hãy copy chính xác phần 'ID' (ví dụ: models/...) dán vào config.py")
    print("="*50)

except Exception as e:
    print(f"❌ Lỗi khi quét danh sách: {e}")