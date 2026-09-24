"""Canonical content state machine.

DB `videos.status` / `ideas.status` must use these values (or legacy aliases).
n8n executions are NOT the source of truth — always persist transitions here.
"""

from __future__ import annotations

from enum import StrEnum


class IdeaStatus(StrEnum):
    NEW = "NEW"
    RESEARCHING = "RESEARCHING"
    IDEAS_READY = "IDEAS_READY"
    TOPIC_PENDING_APPROVAL = "TOPIC_PENDING_APPROVAL"
    TOPIC_APPROVED = "TOPIC_APPROVED"
    TOPIC_REJECTED = "TOPIC_REJECTED"
    TOPIC_REVISION_REQUESTED = "TOPIC_REVISION_REQUESTED"


class VideoStatus(StrEnum):
    NEW = "NEW"
    SCRIPT_GENERATING = "SCRIPT_GENERATING"
    SCRIPT_READY = "SCRIPT_READY"
    SCRIPT_FAILED = "SCRIPT_FAILED"
    MEDIA_GENERATING = "MEDIA_GENERATING"
    MEDIA_READY = "MEDIA_READY"
    MEDIA_FAILED = "MEDIA_FAILED"
    RENDERING = "RENDERING"
    VIDEO_READY = "VIDEO_READY"
    VIDEO_FAILED = "VIDEO_FAILED"
    VIDEO_PENDING_APPROVAL = "VIDEO_PENDING_APPROVAL"
    VIDEO_APPROVED = "VIDEO_APPROVED"
    VIDEO_REJECTED = "VIDEO_REJECTED"
    VIDEO_REVISION_REQUESTED = "VIDEO_REVISION_REQUESTED"
    READY_TO_PUBLISH = "READY_TO_PUBLISH"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    PUBLISH_FAILED = "PUBLISH_FAILED"
    ANALYTICS_COLLECTING = "ANALYTICS_COLLECTING"
    COMPLETED = "COMPLETED"
    # Pipeline operational
    FAILED = "FAILED"


class WorkflowRunStatus(StrEnum):
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    WAITING_PROVIDER = "WAITING_PROVIDER"
    RETRYING = "RETRYING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class ApprovalKind(StrEnum):
    TOPIC = "TOPIC"
    VIDEO = "VIDEO"


class ApprovalDecision(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REVISE = "REVISE"
    NEW_IDEAS = "NEW_IDEAS"
    PUBLISH = "PUBLISH"


# Legacy pipeline statuses still written by automation/jobs.py — map ↔ canonical.
LEGACY_TO_CANONICAL: dict[str, str] = {
    "queued": VideoStatus.NEW,
    "research": VideoStatus.NEW,
    "idea": IdeaStatus.IDEAS_READY,
    "script": VideoStatus.SCRIPT_READY,
    "assets": VideoStatus.MEDIA_READY,
    "voice": VideoStatus.MEDIA_READY,
    "render": VideoStatus.VIDEO_READY,
    "qa": VideoStatus.VIDEO_READY,
    "qa_passed": VideoStatus.VIDEO_READY,
    "qa_failed": VideoStatus.VIDEO_FAILED,
    "awaiting_approval": VideoStatus.VIDEO_PENDING_APPROVAL,
    "approved": VideoStatus.VIDEO_APPROVED,
    "rejected": VideoStatus.VIDEO_REJECTED,
    "uploading": VideoStatus.PUBLISHING,
    "uploaded": VideoStatus.PUBLISHED,
    "failed": VideoStatus.FAILED,
    "ready": VideoStatus.VIDEO_READY,
    "draft": VideoStatus.NEW,
}

# Statuses that may proceed to YouTube upload.
PUBLISHABLE: frozenset[str] = frozenset(
    {
        VideoStatus.VIDEO_APPROVED,
        VideoStatus.READY_TO_PUBLISH,
        "approved",  # legacy
    }
)

# Terminal / locked for resume (no full re-produce).
RESUME_LOCKED: frozenset[str] = frozenset(
    {
        VideoStatus.VIDEO_PENDING_APPROVAL,
        VideoStatus.VIDEO_APPROVED,
        VideoStatus.VIDEO_REJECTED,
        VideoStatus.PUBLISHING,
        VideoStatus.PUBLISHED,
        VideoStatus.COMPLETED,
        "awaiting_approval",
        "approved",
        "rejected",
        "uploading",
        "uploaded",
    }
)


def canonicalize_video_status(status: str) -> str:
    if status in VideoStatus.__members__.values() or status in {s.value for s in VideoStatus}:
        return status
    return LEGACY_TO_CANONICAL.get(status, status)


def can_publish(status: str) -> bool:
    return canonicalize_video_status(status) in {
        VideoStatus.VIDEO_APPROVED,
        VideoStatus.READY_TO_PUBLISH,
    } or status in PUBLISHABLE
