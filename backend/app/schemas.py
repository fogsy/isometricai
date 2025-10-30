from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FrameScore(BaseModel):
    index: int
    timestamp: float
    score: float


class DetectionResponse(BaseModel):
    id: int
    media_type: str
    score: float
    threshold: float
    label: str
    model_name: str
    model_version: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    frames: Optional[List[FrameScore]] = None


class DetectionRequestMetadata(BaseModel):
    filename: Optional[str]
    content_type: Optional[str]
    extras: Dict[str, Any] = Field(default_factory=dict)
