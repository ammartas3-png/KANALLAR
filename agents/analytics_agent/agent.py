from __future__ import annotations

from datetime import datetime, timezone

from automation.logging import log_agent
from database.models import AnalyticsSnapshot, Upload
from database.session import get_session
from youtube.api import YouTubeConfigError, fetch_video_stats


@log_agent("AnalyticsAgent")
def collect(window: str = "24h", **kwargs) -> dict:
    snapshots = 0
    errors = []
    with get_session() as session:
        uploads = session.query(Upload).filter(Upload.youtube_video_id != "").all()
        for row in uploads:
            try:
                stats = fetch_video_stats(row.youtube_video_id)
            except YouTubeConfigError as exc:
                errors.append(str(exc))
                break
            if not stats:
                continue
            session.add(
                AnalyticsSnapshot(
                    video_id=row.video_id,
                    views=stats.get("views", 0),
                    likes=stats.get("likes", 0),
                    comments=stats.get("comments", 0),
                    collected_at=datetime.now(timezone.utc),
                    time_window=window,
                )
            )
            snapshots += 1
    return {"snapshots": snapshots, "errors": errors, "token_usage": 0, "api_cost": 0}
