from __future__ import annotations

from sqlalchemy import func

from database.models import AgentRun
from database.session import get_session


def video_cost(video_id: str) -> float:
    with get_session() as session:
        total = (
            session.query(func.coalesce(func.sum(AgentRun.api_cost), 0))
            .filter(AgentRun.video_id == video_id)
            .scalar()
        )
    return float(total or 0)
