from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANNELS_DIR = ROOT / "channels"
APPS_DIR = ROOT / "apps"
CONTENT_DIR = ROOT / "content"
LOGS_DIR = ROOT / "logs"
MEMORY_DIR = ROOT / "memory"
TEMPLATES_DIR = ROOT / "templates"
REMOTION_DIR = APPS_DIR / "remotion"


def ensure_runtime_dirs() -> None:
    for path in (CONTENT_DIR, LOGS_DIR, MEMORY_DIR, CONTENT_DIR / "videos"):
        path.mkdir(parents=True, exist_ok=True)
