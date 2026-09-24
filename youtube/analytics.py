from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from youtube.api import load_credentials

log = logging.getLogger("kanallar.youtube.analytics")

REPORT_METRICS = "views,likes,comments,shares,subscribersGained,averageViewDuration"


def fetch_video_report(channel_key: str, youtube_video_id: str, days: int = 7) -> dict:
    """YouTube Analytics API v2 totals for one video (filter only, no dimension)."""
    from googleapiclient.discovery import build

    api = build("youtubeAnalytics", "v2", credentials=load_credentials(channel_key))
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    try:
        data = (
            api.reports()
            .query(
                ids="channel==MINE",
                startDate=start.isoformat(),
                endDate=end.isoformat(),
                metrics=REPORT_METRICS,
                filters=f"video=={youtube_video_id}",
            )
            .execute()
        )
    except Exception:
        log.exception("analytics query failed channel=%s video=%s", channel_key, youtube_video_id)
        raise
    headers = [h["name"] for h in data.get("columnHeaders", [])]
    rows = data.get("rows") or []
    if not rows:
        return {}
    return dict(zip(headers, rows[0], strict=False))
