from app.config import settings
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.feedback import router as feedback_router
from app.api.session import router as session_router
from app.utils.logger import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("UIT Chatbot v2.2 đang khởi động...")
    await _auto_init_if_needed()
    from app.services.retrieval import get_db_status
    from app.services.cache import redis_client
    from app.config import settings

    db_status = get_db_status()
    for name, info in db_status.items():
        status = "" if info["loaded"] else ""
        app_logger.info(
            f"  {status} DB [{name.upper()}]: "
            f"{info['total_vectors']} vectors | {info['total_chunks']} chunks"
        )

    all_loaded = all(info["loaded"] for info in db_status.values())
    if not all_loaded:
        app_logger.warning(
            "Một số DB chưa được tạo. "
            "Chạy: python scripts/init_data.py"
        )

    cache_ok = redis_client is not None
    app_logger.info(
        f"  {'' if cache_ok else ''} Redis Cache: "
        f"{'kết nối thành công' if cache_ok else 'offline — chatbot vẫn hoạt động bình thường'}"
    )

    api_ok = bool(settings.GOOGLE_API_KEY)
    app_logger.info(
        f"  {'' if api_ok else ''} Google API Key: "
        f"{'đã cấu hình' if api_ok else 'CHƯA cấu hình — thêm vào .env'}"
    )

    web_ok = settings.WEB_SEARCH_ENABLED
    app_logger.info(f"  {'' if web_ok else ''} Web RAG Fallback: {'bật' if web_ok else 'tắt'}")

    app_logger.info("Server sẵn sàng phục vụ!")
    yield
    app_logger.info("Server đang tắt...")
    
    
async def _auto_init_if_needed():
    """
    Kiểm tra các file FAISS index và chunks.json.
    Nếu thiếu → tự chạy init_data.py để tạo.
    Đây là safety net; bình thường file đã có sẵn trong repo.
    """
    import os, sys
    from app.config import settings

    missing = []
    for scope, faiss_path, chunks_path in [
        ("uit",  settings.FAISS_UIT_PATH,  settings.DATA_UIT_PATH),
        ("cnpm", settings.FAISS_CNPM_PATH, settings.DATA_CNPM_PATH),
    ]:
        if not os.path.exists(faiss_path) or not os.path.exists(chunks_path):
            missing.append(scope)

    if not missing:
        app_logger.info("Tất cả DB đã có sẵn — bỏ qua init")
        return

    app_logger.warning(f"Thiếu DB: {missing} — bắt đầu tự động init...")

    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY.strip() in ("", "your-api-here"):
        app_logger.error("Không thể auto-init: GOOGLE_API_KEY chưa cấu hình trong .env")
        return

    # Thêm scripts/ vào path và gọi build_index trực tiếp
    scripts_dir = os.path.join(settings.BASE_DIR, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    try:
        from init_data import load_raw_data, build_index

        if "uit" in missing:
            app_logger.info("Auto-init DB UIT...")
            data = load_raw_data(settings.RAW_UIT_PATH)
            build_index(data, settings.FAISS_UIT_PATH, settings.DATA_UIT_PATH, scope="uit")

        if "cnpm" in missing:
            app_logger.info("Auto-init DB CNPM...")
            data = load_raw_data(settings.RAW_CNPM_PATH)
            build_index(data, settings.FAISS_CNPM_PATH, settings.DATA_CNPM_PATH, scope="cnpm")

        # Reload DB vào RAM sau khi tạo xong
        from app.services.retrieval import load_all_dbs
        load_all_dbs()
        app_logger.info("Auto-init hoàn tất!")

    except Exception as e:
        app_logger.error(f"Auto-init thất bại: {e}", exc_info=True)


app = FastAPI(
    title="UIT 20 Năm Chatbot API",
    description="Chatbot RAG kỷ niệm 20 năm UIT — hỗ trợ session đa lượt & Web RAG fallback",
    version="2.2.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    settings.FRONTEND_URL,
]
origins = [o for o in origins if o]  # lọc chuỗi rỗng

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
    return {"status": "success", "message": "UIT 20 Years Chatbot API v2.2 🚀"}


@app.get("/health")
def health_check():
    from app.services.retrieval import get_db_status
    from app.services.cache import redis_client
    from app.config import settings

    db_status = get_db_status()
    cache_ok = redis_client is not None
    api_ok = bool(settings.GOOGLE_API_KEY)
    all_dbs_ok = all(info["loaded"] for info in db_status.values())

    return {
        "status": "healthy" if (all_dbs_ok and api_ok) else "degraded",
        "version": "2.2.0",
        "components": {
            "vector_databases": db_status,
            "redis_cache": {
                "connected": cache_ok,
                "note": "Cache tuỳ chọn — chatbot vẫn hoạt động khi Redis offline",
            },
            "google_api": {
                "configured": api_ok,
            },
            "web_rag_fallback": {
                "enabled": settings.WEB_SEARCH_ENABLED,
            },
        },
    }
