import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    GOOGLE_API_KEY: str = ""
    LLM_MODEL: str = "models/gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    MAX_TOKENS: int = 2500
    TEMPERATURE: float = 0.2
    TOP_K_RETRIEVAL: int = 5
    MAX_INPUT_LENGTH: int = 1000
    SIMILARITY_THRESHOLD: float = 200.0

    # Hội thoại & Session
    MAX_HISTORY_TURNS: int = 5

    # Rate Limiting
    RATE_LIMIT_MAX_REQUESTS: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Cache / Session
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 86400

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    RAW_UIT_PATH:  str = os.path.join(BASE_DIR, "data", "raw", "uit",  "data_uit.json")
    RAW_CNPM_PATH: str = os.path.join(BASE_DIR, "data", "raw", "cnpm", "data_cnpm.json")

    FAISS_UIT_PATH:  str = os.path.join(BASE_DIR, "data", "vector_db", "uit_index",  "index.faiss")
    DATA_UIT_PATH:   str = os.path.join(BASE_DIR, "data", "processed", "uit",  "chunks.json")
    FAISS_CNPM_PATH: str = os.path.join(BASE_DIR, "data", "vector_db", "cnpm_index", "index.faiss")
    DATA_CNPM_PATH:  str = os.path.join(BASE_DIR, "data", "processed", "cnpm", "chunks.json")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("GOOGLE_API_KEY")
    @classmethod
    def validate_api_key(cls, v):
        if not v or v.strip() in ("", "your-key-here"):
            raise ValueError("GOOGLE_API_KEY chưa được cấu hình! Thêm vào file .env")
        return v.strip()


settings = Settings()
