# yeu file ma request ra response define garxa 

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

ChunkStrategy = Literal["fixed", "semantic"]


class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_id: str
    filename: str
    chunks_count: int = Field(..., ge=0)


class ChunkStrategyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    strategy: ChunkStrategy = Field(default="fixed")
