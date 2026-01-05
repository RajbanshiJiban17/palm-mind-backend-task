from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from app.core.config import settings
from app.schemes.ingestion import DocumentUploadResponse, ChunkStrategy
from app.services.chunking import get_chunks
from app.services.vector_store import add_chunks_to_vector_db
from app.utils.db import save_document_metadata
from app.utils.text_extractor import TextExtractionError, extract_text_from_file

router = APIRouter()

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    strategy: ChunkStrategy = Form("fixed"),
) -> DocumentUploadResponse:
    filename = (file.filename or "").strip()
    if not filename or not filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are allowed.")

    file_id = str(uuid.uuid4())
    safe_name = filename.replace("/", "_").replace("\\", "_")
    file_path = UPLOAD_DIR / f"{file_id}_{safe_name}"

    try:
        with file_path.open("wb") as f:
            while True:
                part = await file.read(1024 * 1024)
                if not part:
                    break
                f.write(part)
    finally:
        await file.close()

    try:
        text = extract_text_from_file(str(file_path))
    except TextExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text found in the file.")

    chunks = get_chunks(
        text,
        strategy=strategy,
        fixed_size=settings.FIXED_CHUNK_SIZE,
        overlap=settings.FIXED_OVERLAP,
        max_semantic=settings.SEMANTIC_MAX_CHUNK,
    )
    if not chunks:
        raise HTTPException(status_code=400, detail="Chunking produced no chunks.")

    # Persist metadata + vectors
    save_document_metadata(file_id, filename, len(chunks), strategy)
    vectorstore = request.app.state.vectorstore
    add_chunks_to_vector_db(vectorstore, file_id=file_id, chunks=chunks, strategy=strategy)

    return DocumentUploadResponse(file_id=file_id, filename=filename, chunks_count=len(chunks))
