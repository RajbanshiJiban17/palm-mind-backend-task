from __future__ import annotations

import json
from datetime import date, time
from typing import Optional

import ollama
from pydantic import BaseModel, ConfigDict, EmailStr, ValidationError

from app.utils.db import save_booking_record
import os 

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")


class BookingDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    email: EmailStr
    date: date
    time: time


class BookingResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confirmed: bool
    message: str
    details: Optional[BookingDetails] = None


BOOKING_SYSTEM_PROMPT = (
    "You are a booking assistant. Extract booking details from the user message.\n"
    "Return ONLY valid JSON with keys: name, email, date, time.\n"
    "date must be YYYY-MM-DD and time must be HH:MM (24h).\n"
    "If a field is missing, return empty string for that field."
)


def extract_booking_details(user_query: str) -> Optional[BookingDetails]:
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": BOOKING_SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ],
            format="json",
        )
        raw = json.loads(response["message"]["content"])
        raw = {k: (v or "").strip() if isinstance(v, str) else v for k, v in raw.items()}
        if not all(raw.get(k) for k in ("name", "email", "date", "time")):
            return None
        return BookingDetails.model_validate(raw)
    except (json.JSONDecodeError, KeyError, ValidationError):
        return None


def process_booking_request(session_id: str, query: str) -> BookingResult:
    details = extract_booking_details(query)
    if details is None:
        return BookingResult(
            confirmed=False,
            message="Please provide: name, email, YYYY-MM-DD, HH:MM (24hr).",
            details=None,
        )

    save_booking_record(
        session_id=session_id,
        name=details.name,
        email=str(details.email),
        date=str(details.date),
        time=details.time.strftime("%H:%M"),
    )

    return BookingResult(
        confirmed=True,
        message=f"Interview booked for {details.name} on {details.date} at {details.time.strftime('%H:%M')}.",
        details=details,
    )
