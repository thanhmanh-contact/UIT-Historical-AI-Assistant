import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ── Google Gemini API ──────────────────────────────────────────────────────
    GOOGLE_API_KEY: str = ""

    LLM_MODEL: str = "models/gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # ── LLM params ────────────────────────────────────────────────────────────
    MAX_TOKENS: int = 1500           # v2.4: giảm từ 2500 → 1500 (tiết kiệm output token)
    TEMPERATURE: float = 0.2
    TOP_K_RETRIEVAL: int = 3
    MAX_INPUT_LENGTH: int = 1000

    # FAISS L2 distance threshold
    SIMILARITY_THRESHOLD: float = 80.0

    # ── Hội thoại & Session ───────────────────────────────────────────────────
    MAX_HISTORY_TURNS: int = 3     
    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_MAX_REQUESTS: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Cache / Session ───────────────────────────────────────────────────────
    REDIS_URL: str = ""
    CACHE_TTL: int = 86400
    FRONTEND_URL: str = "http://localhost:5173"

    # ── Web RAG ───────────────────────────────────────────────────────────────
    WEB_SEARCH_ENABLED: bool = True
    WEB_SEARCH_TIMEOUT: int = 10
    WEB_SEARCH_MAX_RESULTS: int = 2  # v2.4: giảm từ 3 → 2 (ít trang hơn, đủ context)

    # ── Đường dẫn dữ liệu ─────────────────────────────────────────────────────
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    RAW_UIT_PATH:  str = os.path.join(BASE_DIR, "data", "raw", "uit",  "data_uit.json")
    RAW_CNPM_PATH: str = os.path.join(BASE_DIR, "data", "raw", "cnpm", "data_cnpm.json")

    FAISS_UIT_PATH:  str = os.path.join(BASE_DIR, "data", "vector_db", "uit_index",  "index.faiss")
    DATA_UIT_PATH:   str = os.path.join(BASE_DIR, "data", "processed", "uit",  "chunks.json")

    FAISS_CNPM_PATH: str = os.path.join(BASE_DIR, "data", "vector_db", "cnpm_index", "index.faiss")
    DATA_CNPM_PATH:  str = os.path.join(BASE_DIR, "data", "processed", "cnpm", "chunks.json")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY.strip() in ("", "your-key-here"):
    import warnings
    warnings.warn(
        "GOOGLE_API_KEY chưa được cấu hình. "
        "Thêm GOOGLE_API_KEY=<key> vào file .env để bật tính năng AI.",
        stacklevel=2,
    )
