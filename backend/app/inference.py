from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
from loguru import logger
from PIL import Image

try:
    import torch
    import open_clip
except Exception as exc:  # pragma: no cover - optional dependency handling
    torch = None  # type: ignore
    open_clip = None  # type: ignore
    logger.warning("Optional inference dependencies unavailable: %s", exc)

from .config import settings


class ModelRunner:
    """Encapsulates interaction with the underlying open-source detector."""

    def __init__(self) -> None:
        self.device = settings.device
        self.model_name = settings.model_name
        self.pretrained = settings.model_pretrained
        self.model_version = f"{self.model_name}:{self.pretrained}"
        self.model = None
        self.preprocess = None
        self.linear_weights = np.ones(1, dtype=np.float32)
        self.linear_bias = 0.0
        self._load_model()

    def _load_model(self) -> None:
        if torch is None or open_clip is None:
            logger.warning("Running in degraded mode: CLIP model unavailable")
        else:
            model, _, preprocess = open_clip.create_model_and_transforms(
                self.model_name, pretrained=self.pretrained
            )
            model.eval()
            self.model = model.to(self.device)
            self.preprocess = preprocess
            logger.info("Loaded open_clip model %s", self.model_version)

        weights_path = Path(__file__).resolve().parent.parent / "checkpoints" / "clip_logreg.json"
        if weights_path.exists():
            with weights_path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            self.linear_weights = np.asarray(payload["weights"], dtype=np.float32)
            self.linear_bias = float(payload.get("bias", 0.0))
            logger.info("Loaded custom logistic head from %s", weights_path)
        else:
            dim = (
                int(self.model.text_projection.shape[1])
                if self.model is not None and hasattr(self.model, "text_projection")
                else 512
            )
            rng = np.random.default_rng(42)
            self.linear_weights = rng.normal(size=dim).astype(np.float32)
            self.linear_bias = 0.0
            logger.warning("No logistic head found; using deterministic random weights")

    def _extract_features(self, image: Image.Image) -> np.ndarray:
        if self.model is None or self.preprocess is None or torch is None:
            img_bytes = image.tobytes()
            digest = hashlib.sha256(img_bytes).digest()
            return np.frombuffer(digest, dtype=np.uint8).astype(np.float32)

        with torch.no_grad():
            tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            features = self.model.encode_image(tensor)
            features = features / features.norm(dim=-1, keepdim=True)
            return features.cpu().numpy().squeeze(0)

    def predict_image(self, image: Image.Image) -> float:
        features = self._extract_features(image)
        min_dim = min(features.shape[0], self.linear_weights.shape[0])
        aligned_features = features[:min_dim]
        aligned_weights = self.linear_weights[:min_dim]
        logits = float(np.dot(aligned_features, aligned_weights) + self.linear_bias)
        probability = float(1.0 / (1.0 + np.exp(-logits)))
        logger.debug("Predicted probability=%s", probability)
        return probability

    def predict_frames(self, frames: Iterable[Tuple[int, float, Image.Image]]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for index, timestamp, frame in frames:
            score = self.predict_image(frame)
            results.append({"index": index, "timestamp": timestamp, "score": score})
        return results


runner = ModelRunner()
