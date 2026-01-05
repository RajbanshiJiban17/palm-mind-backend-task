from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    APP_TITLE: str = "Palm Mind RAG Task"

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_SECONDS: int = 60 * 60 * 24

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "palmmind_documents"

    EMBED_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_SIZE: int = 384

    UPLOAD_DIR: str = "uploads"
    DB_PATH: str = "data/app.db"

    FIXED_CHUNK_SIZE: int = 500
    FIXED_OVERLAP: int = 100
    SEMANTIC_MAX_CHUNK: int = 600

    TOP_K: int = 5
    HISTORY_MAX_TURNS: int = 10


settings = Settings()
