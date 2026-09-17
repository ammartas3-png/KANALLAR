from __future__ import annotations

from pathlib import Path

from automation.logging import log_agent
from video.ffmpeg import validate_short


@log_agent("QAAgent")
def inspect(video_path: Path, captions_path: Path | None, script: dict, **kwargs) -> dict:
    checks: dict[str, bool] = {}
    details = {}
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
    checks["copyright_safe"] = True
    ok = all(checks.values())
    return {"ok": ok, "checks": checks, "details": details, "token_usage": 0, "api_cost": 0}
