from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.api.ingestion import router as ingestion_router
from app.api.rag import router as rag_router
from app.core.config import settings
from app.services.vector_store import build_vectorstore
from app.utils.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    app.state.vectorstore = build_vectorstore()
    try:
        yield
    finally:
        await app.state.redis.aclose()


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)

app.include_router(ingestion_router, prefix="/api/v1", tags=["Document Ingestion"])
app.include_router(rag_router, prefix="/api/v2", tags=["Conversational RAG"])


@app.get("/")
async def root():
    return {"status": "Palm Mind Task Live!", "booking": "ready"}
