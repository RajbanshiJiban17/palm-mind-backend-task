from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import List, Optional, Dict

import requests
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

from app.core.config import settings


@dataclass(frozen=True)
class VectorStoreDeps:
    client: QdrantClient
    embedder: SentenceTransformer


def build_vectorstore() -> VectorStoreDeps:
    client = QdrantClient(settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    embedder = SentenceTransformer(settings.EMBED_MODEL)
    return VectorStoreDeps(client=client, embedder=embedder)


def ensure_collection(deps: VectorStoreDeps) -> None:
    # Compatible existence check
    if deps.client.collection_exists(collection_name=settings.QDRANT_COLLECTION):
        return

    deps.client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(size=settings.VECTOR_SIZE, distance=Distance.COSINE),
    )


def add_chunks_to_vector_db(
    deps: VectorStoreDeps,
    file_id: str,
    chunks: List[str],
    strategy: Optional[str] = None,
) -> None:
    if not chunks:
        return

    ensure_collection(deps)
    vectors = deps.embedder.encode(chunks).tolist()

    points: List[models.PointStruct] = []
    for i, (text, vector) in enumerate(zip(chunks, vectors)):
        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),  # valid ID: UUID 
                vector=vector,
                payload={
                    "file_id": file_id,
                    "chunk_index": i,
                    "text": text,
                    "strategy": strategy,
                },
            )
        )

    deps.client.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=points,
        wait=True,
    )


def get_similar_chunks(
    deps: VectorStoreDeps,
    query: str,
    *,
    top_k: int = 5,  # keyword-only avoids multiple values 
) -> List[dict]:
    # Use REST search to avoid client method mismatch samsyaharu
    query_vector = deps.embedder.encode([query]).tolist()[0]

    url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/collections/{settings.QDRANT_COLLECTION}/points/search"
    payload = {"vector": query_vector, "limit": top_k, "with_payload": True}

    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()

    out: List[Dict] = []
    for hit in data.get("result", []):
        out.append(
            {"id": hit.get("id"), "score": hit.get("score"), "payload": hit.get("payload", {})}
        )
    return out
