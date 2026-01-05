from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from redis.asyncio import Redis

from app.core.config import settings
from app.services.booking import process_booking_request
from app.services.vector_store import VectorStoreDeps, get_similar_chunks


def _key(session_id: str) -> str:
    return f"chat:{session_id}"


async def _load_history(redis: Redis, session_id: str) -> List[Dict[str, str]]:
    raw = await redis.get(_key(session_id))
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


async def _save_history(redis: Redis, session_id: str, history: List[Dict[str, str]]) -> None:
    trimmed = history[-settings.HISTORY_MAX_TURNS :]
    await redis.set(_key(session_id), json.dumps(trimmed, ensure_ascii=False), ex=settings.REDIS_TTL_SECONDS)


async def handle_chat_request(
    *,
    redis: Redis,
    vectorstore: VectorStoreDeps,
    session_id: str,
    query: str,
) -> Dict[str, Any]:
    history = await _load_history(redis, session_id)

    chunks = get_similar_chunks(vectorstore, query, top_k=settings.TOP_K)
    context = "\n\n".join(c["payload"].get("text", "") for c in chunks if c.get("payload"))

    prompt = (
        "You are a helpful assistant.\n"
        "Use the context below when relevant.\n\n"
        f"Context:\n{context}\n\n"
        f"Chat History:\n{json.dumps(history, ensure_ascii=False)}\n\n"
        f"User: {query}\n"
    )

    # Replace with real LLM call for answering (Ollama/OpenAI etc.)
    answer = f"Simulated answer for: {query}"

    booking_confirmed = False
    booking_details = None

    if "book" in query.lower() or "interview" in query.lower():
        booking = process_booking_request(session_id=session_id, query=query)
        answer = booking.message
        booking_confirmed = booking.confirmed
        booking_details = booking.details.model_dump() if booking.details else None

    history.append({"user": query, "assistant": answer})
    await _save_history(redis, session_id, history)

    return {
        "response": answer,
        "booking_confirmed": booking_confirmed,
        "booking_details": booking_details,
    }
