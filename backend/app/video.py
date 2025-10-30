from __future__ import annotations

from pathlib import Path
from typing import Generator, Tuple

import cv2
from PIL import Image

from .config import settings


def sample_video_frames(path: Path) -> Generator[Tuple[int, float, Image.Image], None, None]:
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise ValueError(f"Failed to open video: {path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    interval_frames = max(int(fps * settings.frame_sample_rate), 1)

    frame_index = 0
    sampled_index = 0
    while True:
        success, frame = capture.read()
        if not success:
            break
        if frame_index % interval_frames == 0:
            timestamp = frame_index / fps
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb_frame)
            yield sampled_index, timestamp, image
            sampled_index += 1
        frame_index += 1

    capture.release()
