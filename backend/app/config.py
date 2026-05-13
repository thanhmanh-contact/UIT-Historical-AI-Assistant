import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- 1. Cấu hình API Keys & Models ---
    GOOGLE_API_KEY: str = "your-key-here"

    LLM_MODEL: str = "models/gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # --- 2. Cấu hình hệ thống RAG ---
    MAX_TOKENS: int = 2500
    TEMPERATURE: float = 0.2
    TOP_K_RETRIEVAL: int = 5
    MAX_INPUT_LENGTH: int = 1000

    # --- 3. Cấu hình Cache (Redis) ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 86400

    # --- 4. Cấu hình Đường dẫn (Paths) ---
    BASE_DIR: str = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    RAW_UIT_PATH: str = os.path.join(BASE_DIR, "data", "raw", "uit", "data_uit.json")
    RAW_CNPM_PATH: str = os.path.join(BASE_DIR, "data", "raw", "cnpm", "data_cnpm.json")

    # Nhánh UIT
    FAISS_UIT_PATH: str = os.path.join(
        BASE_DIR,
        "data",
        "vector_db",
        "uit_index",
        "index.faiss"
    )

    DATA_UIT_PATH: str = os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "uit",
        "chunks.json"
    )

    # Nhánh CNPM
    FAISS_CNPM_PATH: str = os.path.join(
        BASE_DIR,
        "data",
        "vector_db",
        "cnpm_index",
        "index.faiss"
    )

    DATA_CNPM_PATH: str = os.path.join(
        BASE_DIR,
        "data",
        "processed",
        "cnpm",
        "chunks.json"
    )

    # Pydantic v2
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()