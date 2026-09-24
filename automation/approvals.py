"""Secure human approval tokens for Telegram (and future channels).

Never store raw tokens in the database — only sha256 hashes.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timezone

from database.models import TopicApproval, VideoApproval, utcnow
from database.session import get_session
from database.states import ApprovalDecision, ApprovalKind


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_topic_approval(idea_id: str, channel_id: str = "", actor: str = "telegram") -> dict:
    """Create pending topic approval; returns raw token once (send via Telegram)."""
    token = secrets.token_urlsafe(32)
    row_id = uuid.uuid4().hex[:12]
    with get_session() as session:
        session.add(
            TopicApproval(
                id=row_id,
                idea_id=idea_id,
                channel_id=channel_id,
                decision="",
                actor=actor,
                token_hash=_hash_token(token),
                consumed=False,
            )
        )
    return {
        "approval_id": row_id,
        "kind": ApprovalKind.TOPIC,
        "idea_id": idea_id,
        "token": token,
    }


def issue_video_approval(video_id: str, channel_id: str = "", actor: str = "telegram") -> dict:
    token = secrets.token_urlsafe(32)
    row_id = uuid.uuid4().hex[:12]
    with get_session() as session:
        session.add(
            VideoApproval(
                id=row_id,
                video_id=video_id,
                channel_id=channel_id,
                decision="",
                actor=actor,
                token_hash=_hash_token(token),
                consumed=False,
            )
        )
    return {
        "approval_id": row_id,
        "kind": ApprovalKind.VIDEO,
        "video_id": video_id,
        "token": token,
    }


def consume_topic_approval(
    token: str,
    decision: str,
    feedback: str = "",
) -> dict:
    decision = decision.upper()
    if decision not in {d.value for d in ApprovalDecision}:
        return {"ok": False, "error": "invalid_decision"}
    digest = _hash_token(token)
    with get_session() as session:
        row = (
            session.query(TopicApproval)
            .filter(TopicApproval.token_hash == digest, TopicApproval.consumed.is_(False))
            .first()
        )
        if row is None:
            return {"ok": False, "error": "invalid_or_consumed_token"}
        row.decision = decision
        row.feedback = feedback
        row.consumed = True
        row.decided_at = utcnow()
        return {
            "ok": True,
            "approval_id": row.id,
            "idea_id": row.idea_id,
            "channel_id": row.channel_id,
            "decision": decision,
            "feedback": feedback,
        }


def consume_video_approval(
    token: str,
    decision: str,
    feedback: str = "",
    revision_scope: str = "",
) -> dict:
    decision = decision.upper()
    if decision not in {d.value for d in ApprovalDecision}:
        return {"ok": False, "error": "invalid_decision"}
    digest = _hash_token(token)
    with get_session() as session:
        row = (
            session.query(VideoApproval)
            .filter(VideoApproval.token_hash == digest, VideoApproval.consumed.is_(False))
            .first()
        )
        if row is None:
            return {"ok": False, "error": "invalid_or_consumed_token"}
        row.decision = decision
        row.feedback = feedback
        row.revision_scope = revision_scope
        row.consumed = True
        row.decided_at = utcnow()
        return {
            "ok": True,
            "approval_id": row.id,
            "video_id": row.video_id,
            "channel_id": row.channel_id,
            "decision": decision,
            "feedback": feedback,
            "revision_scope": revision_scope,
        }


def has_valid_video_publish_approval(video_id: str) -> bool:
    """True if a consumed VIDEO approval with PUBLISH or APPROVE exists."""
    with get_session() as session:
        row = (
            session.query(VideoApproval)
            .filter(
                VideoApproval.video_id == video_id,
                VideoApproval.consumed.is_(True),
                VideoApproval.decision.in_(
                    [ApprovalDecision.PUBLISH, ApprovalDecision.APPROVE]
                ),
            )
            .order_by(VideoApproval.decided_at.desc())
            .first()
        )
        return row is not None


def constant_time_token_match(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())
