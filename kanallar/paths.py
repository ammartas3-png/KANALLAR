from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANNELS_DIR = ROOT / "channels"
PACKAGE_DIR = Path(__file__).resolve().parent
CATALOG_DIR = PACKAGE_DIR / "catalog"
WEB_DIR = PACKAGE_DIR / "web"


def data_dir() -> Path:
    raw = os.environ.get("KANALLAR_DATA", str(ROOT / "data"))
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def jobs_dir() -> Path:
    path = data_dir() / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / "kanallar.db"


def job_dir(job_id: str) -> Path:
    path = jobs_dir() / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path
