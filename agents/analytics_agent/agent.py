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
            report: dict = {}
            try:
                from youtube.analytics import fetch_video_report

                report = fetch_video_report(row.youtube_video_id) or {}
            except Exception as exc:
                errors.append(f"analytics:{exc}")
            try:
                stats = fetch_video_stats(row.youtube_video_id)
            except YouTubeConfigError as exc:
                errors.append(str(exc))
                break
            if not stats and not report:
                continue
            session.add(
                AnalyticsSnapshot(
                    video_id=row.video_id,
                    views=int(report.get("views") or stats.get("views") or 0),
                    likes=int(report.get("likes") or stats.get("likes") or 0),
                    comments=int(report.get("comments") or stats.get("comments") or 0),
                    shares=int(report.get("shares") or 0),
                    subscribers_gained=int(report.get("subscribersGained") or 0),
                    average_view_duration=float(report.get("averageViewDuration") or 0),
                    collected_at=datetime.now(timezone.utc),
                    time_window=window,
                )
            )
            snapshots += 1
    return {"snapshots": snapshots, "errors": errors, "token_usage": 0, "api_cost": 0}
