from pathlib import Path

from backend.app.utils import hash_bytes, hash_file, save_upload_to_disk


def test_hash_bytes_stable() -> None:
    data = b"hello world"
    assert hash_bytes(data) == hash_bytes(data)


def test_save_upload_and_hash(tmp_path: Path) -> None:
    destination = tmp_path / "sample.bin"
    save_upload_to_disk(DummyIO(b"payload"), destination)
    assert destination.exists()
    assert hash_file(destination) == hash_bytes(b"payload")


class DummyIO:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self._offset = 0

    def read(self, size: int) -> bytes:
        if self._offset >= len(self._payload):
            return b""
        chunk = self._payload[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk
