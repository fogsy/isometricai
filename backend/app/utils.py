from __future__ import annotations

import hashlib
from pathlib import Path
from typing import IO


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(8192), b''):
            digest.update(chunk)
    return digest.hexdigest()


def save_upload_to_disk(data: IO[bytes], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('wb') as fh:
        while True:
            chunk = data.read(8192)
            if not chunk:
                break
            fh.write(chunk)
    return destination
