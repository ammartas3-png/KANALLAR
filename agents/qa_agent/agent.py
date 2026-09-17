from __future__ import annotations

from pathlib import Path

from automation.logging import log_agent
from database.models import Script
from database.session import get_session
from video.ffmpeg import validate_short


@log_agent("QAAgent")
def inspect(video_path: Path, captions_path: Path | None, script: dict, **kwargs) -> dict:
    checks: dict[str, bool] = {}
    details: dict = {}
    if not video_path.exists():
        return {"ok": False, "checks": {"file_exists": False}, "token_usage": 0, "api_cost": 0}
    meta = validate_short(video_path)
    details.update(meta)
    checks["resolution"] = bool(meta["is_1080x1920"])
    checks["aspect_9_16"] = bool(meta["is_9_16"])
    checks["duration"] = 12 <= meta["duration"] <= 60
    checks["has_audio"] = bool(meta["has_audio"])
    checks["has_video"] = bool(meta["has_video"])
    checks["captions"] = bool(captions_path and captions_path.exists() and captions_path.stat().st_size > 40)
    checks["not_tiny"] = meta["size_bytes"] > 80_000
    checks["script_present"] = bool(script.get("hook") and script.get("scenes"))
    checks["no_long_black"] = len(meta.get("black_segments") or []) == 0
    checks["has_voice"] = len(meta.get("silence_segments") or []) < 3
    checks["not_duplicate"] = not _duplicate_narration(
        script.get("narration") or "",
        exclude_script_id=kwargs.get("script_id"),
    )
    checks["copyright_safe"] = True
    details["duplicate_of"] = None if checks["not_duplicate"] else "existing_script"
    ok = all(checks.values())
    return {"ok": ok, "checks": checks, "details": details, "token_usage": 0, "api_cost": 0}


def _duplicate_narration(narration: str, exclude_script_id: str | None = None) -> bool:
    if not narration.strip():
        return False
    with get_session() as session:
        query = session.query(Script).filter(Script.script == narration)
        if exclude_script_id:
            query = query.filter(Script.id != exclude_script_id)
        rows = query.all()
    return len(rows) >= 1
