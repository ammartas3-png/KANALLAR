from __future__ import annotations

from typing import Protocol


class ObjectStorage(Protocol):
    name: str

    def configured(self) -> bool: ...

    def put_file(self, key: str, path: str, content_type: str = "application/octet-stream") -> str: ...

    def public_url(self, key: str) -> str: ...
