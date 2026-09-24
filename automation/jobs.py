from __future__ import annotations

import json
from typing import Any

from database.models import Video
from database.session import get_session
from database.states import RESUME_LOCKED, VideoStatus


STAGES = [
    "research",
    "idea",
    "script",
    "assets",
    "voice",
    "render",
    "qa",
    "awaiting_approval",
    "approved",
    "rejected",
    "uploading",
    "uploaded",
    "failed",
    VideoStatus.VIDEO_PENDING_APPROVAL,
    VideoStatus.VIDEO_APPROVED,
    VideoStatus.VIDEO_REJECTED,
    VideoStatus.PUBLISHING,
    VideoStatus.PUBLISHED,
]

# Resume must not re-enter post-QA / upload for these statuses (duplicate publish risk).
RESUME_LOCKED_STATUSES = RESUME_LOCKED


def load_checkpoint(video_id: str) -> dict[str, Any]:
    with get_session() as session:
        row = session.get(Video, video_id)
        if row is None:
            return {}
        try:
            qa = json.loads(row.qa_json or "{}")
        except json.JSONDecodeError:
            qa = {}
        return {
            "id": row.id,
            "status": row.status,
            "stage": qa.get("stage") or row.status,
            "completed_stages": qa.get("completed_stages") or [],
            "filepath": row.filepath,
            "qa": qa,
            "channel_id": row.channel_id,
            "script_id": row.script_id,
        }


def save_checkpoint(video_id: str, stage: str, **extra: Any) -> None:
    with get_session() as session:
        row = session.get(Video, video_id)
        if row is None:
            return
        try:
            qa = json.loads(row.qa_json or "{}")
        except json.JSONDecodeError:
            qa = {}
        completed = list(qa.get("completed_stages") or [])
        if stage not in completed and stage not in {"failed", "awaiting_approval", "rejected"}:
            completed.append(stage)
        qa["stage"] = stage
        qa["completed_stages"] = completed
        for key, value in extra.items():
            qa[key] = value
        row.qa_json = json.dumps(qa, ensure_ascii=False)
        row.status = stage
        if "filepath" in extra and extra["filepath"]:
            row.filepath = str(extra["filepath"])
        if "duration" in extra and extra["duration"] is not None:
            row.duration = float(extra["duration"])


def mark_failed(video_id: str, stage: str, error: str) -> None:
    save_checkpoint(video_id, "failed", failed_stage=stage, error=error)


def list_awaiting_approval(limit: int = 50) -> list[dict[str, Any]]:
    with get_session() as session:
        rows = (
            session.query(Video)
            .filter(
                Video.status.in_(
                    ["awaiting_approval", VideoStatus.VIDEO_PENDING_APPROVAL]
                )
            )
            .order_by(Video.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": row.id,
                "channel_id": row.channel_id,
                "filepath": row.filepath,
                "duration": row.duration,
                "created_at": row.created_at.isoformat() if row.created_at else "",
            }
            for row in rows
        ]


def approve_video(video_id: str) -> dict[str, Any]:
    checkpoint = load_checkpoint(video_id)
    if not checkpoint:
        return {"ok": False, "error": "video_not_found", "id": video_id}
    allowed = {
        "awaiting_approval",
        "qa",
        "qa_passed",
        VideoStatus.VIDEO_PENDING_APPROVAL,
        VideoStatus.VIDEO_READY,
    }
    if checkpoint["status"] not in allowed:
        return {
            "ok": False,
            "error": "not_awaiting_approval",
            "id": video_id,
            "status": checkpoint["status"],
        }
    save_checkpoint(video_id, VideoStatus.VIDEO_APPROVED, approved=True)
    return {"ok": True, "id": video_id, "status": VideoStatus.VIDEO_APPROVED}


def reject_video(video_id: str, reason: str = "") -> dict[str, Any]:
    checkpoint = load_checkpoint(video_id)
    if not checkpoint:
        return {"ok": False, "error": "video_not_found", "id": video_id}
    save_checkpoint(video_id, VideoStatus.VIDEO_REJECTED, approved=False, reject_reason=reason)
    return {"ok": True, "id": video_id, "status": VideoStatus.VIDEO_REJECTED, "reason": reason}
