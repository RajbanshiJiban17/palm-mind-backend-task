from __future__ import annotations

from datetime import date, time
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookingDetailsSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    email: EmailStr
    date: date
    time: time


class RequestChatSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    query: str = Field(..., min_length=1)


class ResponseChatSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    response: str
    booking_confirmed: bool = False
    booking_details: Optional[BookingDetailsSchema] = None
