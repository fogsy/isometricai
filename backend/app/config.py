from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=('.env', '.env.local'), env_nested_delimiter='__')

    database_url: str = "sqlite:///" + str(Path(__file__).resolve().parent.parent / "app.db")
    allowed_origins: List[str] = ["*"]
    media_tmp_dir: Path = Path("/tmp/media")
    frame_sample_rate: float = 1.0  # seconds between sampled frames
    default_threshold: float = 0.5
    model_name: str = "ViT-B-32"
    model_pretrained: str = "laion2b_s34b_b79k"
    device: str = "cpu"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
settings.media_tmp_dir.mkdir(parents=True, exist_ok=True)
