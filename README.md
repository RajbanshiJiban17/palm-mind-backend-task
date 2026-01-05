# Palm Mind Backend Task (FastAPI)

I built two APIs:
- Document upload (.pdf/.txt) → chunk text → create embeddings → store in Qdrant
- Chat API with Redis memory (multi-turn) + interview booking saved to SQLite

## Why these tools
- Qdrant: vector similarity search for RAG context.
- Redis: simple per-session chat history with TTL.
- SQLite: easy local storage for metadata and bookings.

## How to run

### 1) Start Redis + Qdrant
```bash
docker compose up -d


“Default model: llama3.2:1b (low RAM friendly). To use another model, change OLLAMA_MODEL.”
​

“If you get model requires more system memory, pick a smaller model tag.”
​

“When calling Ollama, request uses JSON body and stream:false to avoid streaming parsing issues.”