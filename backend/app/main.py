from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.feedback import router as feedback_router

# 1. Khởi tạo FastAPI app
app = FastAPI(
    title="Khám phá 20 năm UIT - Chatbot API",
    description="API cho hệ thống chatbot RAG tìm hiểu lịch sử UIT",
    version="1.0.0"
)

# 2. Cấu hình CORS (Bắt buộc để Frontend React có thể gọi API)
origins =[
    "http://localhost:3000",  # Default React/Vite port
    "http://localhost:5173",  # Default Vite port
    # Thêm các domain frontend của bạn khi deploy lên host thật
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Cho phép GET, POST, PUT, DELETE...
    allow_headers=["*"],
)

# 3. Đăng ký các Router
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(feedback_router, prefix="/api/v1", tags=["Feedback"])

# 4. Health Check Endpoint (Dùng để kiểm tra server có đang sống không)
@app.get("/")
def read_root():
    return {
        "status": "success",
        "message": "Welcome to UIT 20 Years Chatbot API! 🚀"
    }

# Lệnh chạy server (chạy trong terminal tại thư mục backend/):
# uvicorn app.main:app --reload --port 8000