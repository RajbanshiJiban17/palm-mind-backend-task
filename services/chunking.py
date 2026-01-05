from __future__ import annotations

import re
from typing import List, Literal, TypeAlias

ChunkStrategy: TypeAlias = Literal["fixed", "semantic"]


def chunk_text_fixed_size(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Split text into fixed-size chunks with overlap."""
    text = (text or "").strip()
    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0.")
    if overlap < 0:
        raise ValueError("overlap must be >= 0.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    chunks: List[str] = []
    start = 0
    n = len(text)

    step = chunk_size - overlap
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += step

    return chunks


_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")  # blank-line paragraph split [web:163]


def semantic_chunking(text: str, max_chunk_size: int = 600) -> List[str]:
    """Split text on paragraph boundaries and pack into chunks up to max_chunk_size."""
    text = (text or "").strip()
    if not text:
        return []

    if max_chunk_size <= 0:
        raise ValueError("max_chunk_size must be > 0.")

    paragraphs = [p.strip() for p in _PARAGRAPH_SPLIT_RE.split(text) if p.strip()]  # [web:163]
    chunks: List[str] = []
    current: list[str] = []
    current_len = 0

    def flush() -> None:
        nonlocal current, current_len
        if current:
            chunks.append(" ".join(current).strip())
            current = []
            current_len = 0

    for p in paragraphs:
        # If a single paragraph is too large, fall back to fixed split for that paragraph
        if len(p) > max_chunk_size:
            flush()
            chunks.extend(chunk_text_fixed_size(p, chunk_size=max_chunk_size, overlap=0))
            continue

        extra = len(p) + (1 if current else 0)
        if current_len + extra > max_chunk_size:
            flush()

        current.append(p)
        current_len += extra

    flush()
    return chunks


def get_chunks(
    text: str,
    strategy: ChunkStrategy = "fixed",
    *,
    fixed_size: int = 500,
    overlap: int = 100,
    max_semantic: int = 600,
) -> List[str]:
    if strategy == "fixed":
        return chunk_text_fixed_size(text, chunk_size=fixed_size, overlap=overlap)
    if strategy == "semantic":
        return semantic_chunking(text, max_chunk_size=max_semantic)
    raise ValueError("strategy must be 'fixed' or 'semantic'.")