from __future__ import annotations

from pathlib import Path

from config.settings import get_settings
from storage.base import ObjectStorage
from storage.local import LocalStorage
from storage.s3 import S3Storage


def get_storage() -> ObjectStorage:
    settings = get_settings()
    backend = (settings.storage_backend or "local").lower()
    if backend == "s3":
        store = S3Storage()
        if store.configured():
            return store
        # Misconfigured cloud → fail loud rather than silently use ephemeral disk
        if settings.run_mode == "cloud":
            raise RuntimeError(
                "RUN_MODE=cloud ve STORAGE_BACKEND=s3 ama bucket/key yok. "
                "R2/S3 secret'larını platform env'e ekleyin."
            )
        return LocalStorage()
    return LocalStorage()


def sync_video_artifacts(video_id: str, video_path: Path, thumb_path: Path | None = None) -> dict:
    """Upload final mp4 (+ thumb) to object storage; return URLs."""
    store = get_storage()
    out: dict = {"backend": store.name, "urls": {}}
    if video_path.exists():
        key = f"videos/{video_id}/final.mp4"
        out["urls"]["video"] = store.put_file(key, str(video_path), "video/mp4")
    if thumb_path and Path(thumb_path).exists():
        key = f"videos/{video_id}/thumbnail.png"
        out["urls"]["thumb"] = store.put_file(key, str(thumb_path), "image/png")
    return out


def storage_status() -> dict:
    settings = get_settings()
    local = LocalStorage()
    s3 = S3Storage()
    return {
        "run_mode": settings.run_mode,
        "backend": settings.storage_backend,
        "local": {"configured": local.configured()},
        "s3": {"configured": s3.configured(), "bucket": bool(settings.storage_bucket)},
    }
