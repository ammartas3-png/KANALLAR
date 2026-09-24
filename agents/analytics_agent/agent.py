from __future__ import annotations

import logging
from datetime import datetime, timezone

from automation.logging import log_agent
from database.models import AnalyticsSnapshot, Upload, Video
from database.session import get_session
from youtube.api import YouTubeConfigError, fetch_video_stats
from youtube.guard import ChannelGuardError

log = logging.getLogger("kanallar.analytics")


@log_agent("AnalyticsAgent")
def collect(window: str = "24h", **kwargs) -> dict:
    from youtube.analytics import fetch_video_report

    snapshots = 0
    errors: list[str] = []
    unavailable: set[str] = set()
    with get_session() as session:
        rows = (
            session.query(Upload, Video.channel_id)
            .join(Video, Video.id == Upload.video_id)
            .filter(Upload.youtube_video_id != "")
            .all()
        )
        for upload, channel_key in rows:
            if channel_key in unavailable:
                continue
            report: dict = {}
            try:
                report = fetch_video_report(channel_key, upload.youtube_video_id) or {}
            except (YouTubeConfigError, ChannelGuardError) as exc:
                errors.append(f"{channel_key}:{exc}")
                unavailable.add(channel_key)
                continue
            except Exception as exc:
                log.exception("analytics report failed video=%s", upload.youtube_video_id)
                errors.append(f"analytics:{upload.youtube_video_id}:{exc}")
            try:
                stats = fetch_video_stats(channel_key, upload.youtube_video_id)
            except (YouTubeConfigError, ChannelGuardError) as exc:
                errors.append(f"{channel_key}:{exc}")
                unavailable.add(channel_key)
                continue
            if not stats and not report:
                continue
            session.add(
                AnalyticsSnapshot(
                    video_id=upload.video_id,
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
