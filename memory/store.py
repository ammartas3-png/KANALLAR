from __future__ import annotations

from database.models import MemoryItem, UsedTopic
from database.session import get_session


def remember(channel_id: str, type_: str, key: str, value: str, confidence: float = 0.5) -> None:
    with get_session() as session:
        session.add(
            MemoryItem(channel_id=channel_id, type=type_, key=key, value=value, confidence=confidence)
        )


def recall(channel_id: str, type_: str | None = None) -> list[MemoryItem]:
    with get_session() as session:
        query = session.query(MemoryItem).filter(MemoryItem.channel_id == channel_id)
        if type_:
            query = query.filter(MemoryItem.type == type_)
        return list(query.order_by(MemoryItem.updated_at.desc()).all())


def used_topics(channel_id: str) -> set[str]:
    with get_session() as session:
        rows = session.query(UsedTopic).filter(UsedTopic.channel_id == channel_id).all()
        return {row.topic_key for row in rows}


def mark_used(channel_id: str, topic_key: str) -> None:
    with get_session() as session:
        session.add(UsedTopic(channel_id=channel_id, topic_key=topic_key))


def profile(channel_id: str) -> dict[str, list[str]]:
    items = recall(channel_id)
    grouped: dict[str, list[str]] = {}
    for item in items:
        grouped.setdefault(item.type, []).append(f"{item.key}={item.value}")
    return grouped
