from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String

from .database import Base


class DetectionResult(Base):
    __tablename__ = "detection_results"

    id: int = Column(Integer, primary_key=True, index=True)
    media_type: str = Column(String, nullable=False)
    media_hash: str = Column(String, nullable=False, index=True)
    score: float = Column(Float, nullable=False)
    threshold: float = Column(Float, nullable=False)
    label: str = Column(String, nullable=False)
    model_name: str = Column(String, nullable=False)
    model_version: str = Column(String, nullable=False)
    metadata: Optional[dict] = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
