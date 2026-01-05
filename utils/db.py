from __future__ import annotations

import os
import sqlite3
from typing import Optional

from app.core.config import settings

os.makedirs("data", exist_ok=True)


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(settings.DB_PATH)


def init_db() -> None:
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                file_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                chunks_count INTEGER NOT NULL,
                strategy TEXT NOT NULL,
                upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_document_metadata(file_id: str, filename: str, chunks_count: int, strategy: str) -> None:
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO documents (file_id, filename, chunks_count, strategy)
            VALUES (?, ?, ?, ?)
            """,
            (file_id, filename, chunks_count, strategy),
        )


def save_booking_record(session_id: str, name: str, email: str, date: str, time: str) -> None:
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO bookings (session_id, name, email, date, time)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, name, email, date, time),
        )
