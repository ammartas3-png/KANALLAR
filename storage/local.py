from __future__ import annotations

import shutil
from pathlib import Path

from config.paths import CONTENT_DIR


class LocalStorage:
    """Ephemeral disk under content/ — OK for CI/smoke, not production durability."""

    name = "local"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or (CONTENT_DIR / "object_store")
        self.root.mkdir(parents=True, exist_ok=True)

    def configured(self) -> bool:
        return True

    def put_file(self, key: str, path: str, content_type: str = "application/octet-stream") -> str:
        dest = self.root / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
        return self.public_url(key)

    def public_url(self, key: str) -> str:
        return str((self.root / key).resolve())
