"""Hybrid-factory topic research: signals in, shortlist out — no media spend."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timedelta, timezone

import yaml

from channels.loader import load_channel
from config.settings import get_settings
from database.models import Idea, UsedTopic
from database.session import get_session, init_db
from database.states import IdeaStatus
from memory.store import used_topics
from research.trends import wikipedia_most_read


def _id() -> str:
    return uuid.uuid4().hex[:12]


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]{3,}", (text or "").lower())}


def _similar(a: str, b: str, threshold: float = 0.55) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return False
    overlap = len(ta & tb) / max(1, min(len(ta), len(tb)))
    return overlap >= threshold


def _recent_topics(channel_id: str, days: int) -> list[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    with get_session() as session:
        used = [
            row.topic_key
            for row in session.query(UsedTopic)
            .filter(UsedTopic.channel_id == channel_id)
            .all()
            if row.created_at is None or row.created_at.replace(tzinfo=timezone.utc) >= cutoff
        ]
        ideas = [
            row.topic
            for row in session.query(Idea)
            .filter(Idea.channel_id == channel_id)
            .order_by(Idea.created_at.desc())
            .limit(80)
            .all()
            if row.created_at is None or (row.created_at.replace(tzinfo=timezone.utc) >= cutoff)
        ]
    return used + ideas


def generate_topic_candidates(channel_id: str | None = None, limit: int = 15) -> dict:
    """Build 10–20 candidates with stored ranking signals (no LLM viral fantasy)."""
    init_db()
    settings = get_settings()
    channel = load_channel(channel_id)
    from automation.pipeline import seed_channel

    seed_channel(channel)
    catalog = yaml.safe_load(channel.catalog_path().read_text(encoding="utf-8")) or []
    used = used_topics(channel.id)
    cooldown_days = settings.topic_similarity_cooldown_days
    recent = _recent_topics(channel.id, cooldown_days)
    trends = wikipedia_most_read(channel.language)
    trend_titles = {row.get("title", "").lower() for row in trends if row.get("title")}

    candidates: list[dict] = []
    for item in catalog:
        topic = item.get("title") or ""
        topic_key = item.get("id") or topic
        recently_used = topic_key in used or any(_similar(topic, r) for r in recent)
        if recently_used and topic_key in used:
            # Hard skip exact used ids; soft-penalize similar below
            continue

        trend_hit = topic.lower() in trend_titles or any(
            _similar(topic, t, 0.45) for t in trend_titles
        )
        competition_signal = 0.3  # reserved; yt-dlp only later for top shortlist
        novelty = 0.9 if topic_key not in used else 0.2
        if any(_similar(topic, r) for r in recent):
            novelty *= 0.4
        channel_fit = 0.85
        visual = 0.7 if item.get("visual") else 0.55
        # Weighted score — weights are explicit, not "AI vibes"
        score = (
            0.35 * novelty
            + 0.25 * (0.9 if trend_hit else 0.35)
            + 0.15 * channel_fit
            + 0.15 * visual
            + 0.10 * (1.0 - competition_signal)
        )
        candidates.append(
            {
                "topic_id": topic_key,
                "topic": topic,
                "angle": item.get("visual") or channel.niche,
                "hook_candidate": item.get("hook") or topic,
                "source": "catalog+wikipedia_most_read",
                "trend_signal": bool(trend_hit),
                "competition_signal": competition_signal,
                "channel_fit": channel_fit,
                "novelty": round(novelty, 3),
                "recently_used": recently_used,
                "estimated_visual_potential": visual,
                "score": round(score, 4),
                "signals": {
                    "in_most_read": trend_hit,
                    "unused_catalog": topic_key not in used,
                    "cooldown_days": cooldown_days,
                },
                "facts": item.get("facts") or [],
                "closer": item.get("closer") or "",
                "tags": item.get("tags") or [],
                "visual": item.get("visual") or "",
            }
        )

    candidates.sort(key=lambda c: c["score"], reverse=True)
    pool = candidates[: max(10, min(limit, 20))]
    shortlist = [c for c in pool if not c["recently_used"]][:5] or pool[:3]

    idea_ids: list[str] = []
    with get_session() as session:
        for cand in shortlist:
            idea_id = _id()
            idea_ids.append(idea_id)
            session.add(
                Idea(
                    id=idea_id,
                    channel_id=channel.id,
                    topic=cand["topic"],
                    source=cand["source"],
                    score=float(cand["score"]),
                    status=IdeaStatus.TOPIC_PENDING_APPROVAL,
                    angle=cand["angle"],
                    hook_candidate=cand["hook_candidate"],
                    payload_json=json.dumps({**cand, "idea_id": idea_id}, ensure_ascii=False),
                )
            )
            cand["idea_id"] = idea_id

    return {
        "channel_id": channel.id,
        "channel_name": channel.name,
        "candidate_count": len(pool),
        "candidates": pool,
        "shortlist": shortlist,
        "idea_ids": idea_ids,
        "status": IdeaStatus.TOPIC_PENDING_APPROVAL,
        "strategy": "hybrid_low_cost",
        "note": "Media/Kie is NOT started until topic APPROVE.",
    }


def get_pending_topics(channel_id: str | None = None, limit: int = 10) -> list[dict]:
    init_db()
    channel = load_channel(channel_id)
    with get_session() as session:
        rows = (
            session.query(Idea)
            .filter(
                Idea.channel_id == channel.id,
                Idea.status == IdeaStatus.TOPIC_PENDING_APPROVAL,
            )
            .order_by(Idea.score.desc())
            .limit(limit)
            .all()
        )
        out = []
        for row in rows:
            try:
                payload = json.loads(row.payload_json or "{}")
            except json.JSONDecodeError:
                payload = {}
            out.append(
                {
                    "idea_id": row.id,
                    "topic": row.topic,
                    "angle": row.angle,
                    "hook_candidate": row.hook_candidate,
                    "score": row.score,
                    "status": row.status,
                    "payload": payload,
                }
            )
        return out
