from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from .config import settings
from .database import Base, engine, get_session
from .inference import runner
from .models import DetectionResult
from .schemas import DetectionRequestMetadata, DetectionResponse, FrameScore
from .utils import hash_bytes, hash_file, save_upload_to_disk
from .video import sample_video_frames

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Media Authenticity Detector", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _persist_result(
    *,
    media_type: str,
    score: float,
    frames: List[FrameScore] | None,
    metadata: Dict[str, Any] | None,
    media_hash: str,
    threshold: float,
) -> DetectionResponse:
    label = "synthetic" if score >= threshold else "real"
    with get_session() as session:
        record = DetectionResult(
            media_type=media_type,
            media_hash=media_hash,
            score=score,
            threshold=threshold,
            label=label,
            model_name=runner.model_name,
            model_version=runner.model_version,
            metadata=(metadata or {}) | {"frames": [frame.model_dump() for frame in frames] if frames else None},
        )
        session.add(record)
        session.flush()
        created_at = record.created_at or datetime.utcnow()
        response = DetectionResponse(
            id=record.id,
            media_type=media_type,
            score=score,
            threshold=threshold,
            label=label,
            model_name=runner.model_name,
            model_version=runner.model_version,
            created_at=created_at,
            metadata=metadata,
            frames=frames,
        )
    return response


@app.post("/detect/image", response_model=DetectionResponse)
async def detect_image(
    file: UploadFile = File(...),
    threshold: float = settings.default_threshold,
) -> DetectionResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")

    raw_bytes = await file.read()
    try:
        image = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    except Exception as exc:  # pragma: no cover - PIL specific errors
        raise HTTPException(status_code=400, detail=f"Unable to parse image: {exc}") from exc

    score = runner.predict_image(image)
    media_hash = hash_bytes(raw_bytes)
    metadata = DetectionRequestMetadata(filename=file.filename, content_type=file.content_type).model_dump()
    return _persist_result(
        media_type="image",
        score=score,
        frames=None,
        metadata=metadata,
        media_hash=media_hash,
        threshold=threshold,
    )


@app.post("/detect/video", response_model=DetectionResponse)
async def detect_video(
    file: UploadFile = File(...),
    threshold: float = settings.default_threshold,
) -> DetectionResponse:
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a video")

    tmp_path = settings.media_tmp_dir / f"{hash_bytes(file.filename.encode('utf-8') if file.filename else b'video')}"
    save_upload_to_disk(file.file, tmp_path)
    media_hash = hash_file(tmp_path)

    frames_raw = list(sample_video_frames(tmp_path))
    if not frames_raw:
        raise HTTPException(status_code=422, detail="No frames extracted from video")

    frames = [FrameScore(**frame) for frame in runner.predict_frames(frames_raw)]
    aggregate_score = float(sum(frame.score for frame in frames) / len(frames))
    metadata = DetectionRequestMetadata(filename=file.filename, content_type=file.content_type).model_dump()
    response = _persist_result(
        media_type="video",
        score=aggregate_score,
        frames=frames,
        metadata=metadata,
        media_hash=media_hash,
        threshold=threshold,
    )
    tmp_path.unlink(missing_ok=True)
    return response


@app.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "ok",
        "model_version": runner.model_version,
        "threshold": settings.default_threshold,
    }
