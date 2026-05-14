from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.feedback import router as feedback_router
from app.api.session import router as session_router
from app.utils.logger import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("🚀 UIT Chatbot đang khởi động...")
    from app.services.retrieval import get_db_status
    from app.services.cache import redis_client
    db_status = get_db_status()
    for name, info in db_status.items():
        status = "✅" if info["loaded"] else "❌"
        app_logger.info(f"  {status} DB [{name.upper()}]: {info['total_vectors']} vectors | {info['total_chunks']} chunks")
    cache_ok = redis_client is not None
    app_logger.info(f"  {'✅' if cache_ok else '⚠️'} Redis Cache: {'kết nối thành công' if cache_ok else 'không kết nối (fallback in-memory)'}")
    app_logger.info("✅ Server sẵn sàng!")
    yield
    app_logger.info("🛑 Server đang tắt...")


app = FastAPI(
    title="UIT 20 Năm Chatbot API",
    description="Chatbot RAG kỷ niệm 20 năm UIT với hỗ trợ session đa lượt",
    version="2.1.0",
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router,     prefix="/api/v1", tags=["Chat"])
app.include_router(feedback_router, prefix="/api/v1", tags=["Feedback"])
app.include_router(session_router,  prefix="/api/v1", tags=["Session"])


@app.get("/")
def read_root():
    return {"status": "success", "message": "UIT 20 Years Chatbot API v2.1 🚀"}


@app.get("/health")
def health_check():
    from app.services.retrieval import get_db_status
    from app.services.cache import redis_client
    db_status = get_db_status()
    cache_ok = redis_client is not None
    all_dbs_ok = all(info["loaded"] for info in db_status.values())
    return {
        "status": "healthy" if all_dbs_ok else "degraded",
        "components": {
            "vector_databases": db_status,
            "redis_cache": {
                "connected": cache_ok,
                "note": "Cache tuỳ chọn — chatbot vẫn hoạt động khi Redis offline"
            }
        }
    }
