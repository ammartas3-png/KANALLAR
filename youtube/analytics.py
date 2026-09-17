from __future__ import annotations

from datetime import date, timedelta

from youtube.api import YouTubeConfigError, _token


def fetch_video_report(youtube_video_id: str, days: int = 7) -> dict:
    """YouTube Analytics API v2. Needs yt-analytics.readonly scope + token."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    if not _token().exists():
        raise YouTubeConfigError("YouTube Analytics için token yok")
    creds = Credentials.from_authorized_user_file(str(_token()))
    api = build("youtubeAnalytics", "v2", credentials=creds)
    end = date.today()
    start = end - timedelta(days=days)
    data = (
        api.reports()
        .query(
            ids="channel==MINE",
            startDate=start.isoformat(),
            endDate=end.isoformat(),
            metrics="views,likes,comments,shares,subscribersGained,averageViewDuration,annotationClickThroughRate",
            dimensions="video",
            filters=f"video=={youtube_video_id}",
        )
        .execute()
    )
    headers = [h["name"] for h in data.get("columnHeaders", [])]
    rows = data.get("rows") or []
    if not rows:
        return {}
    return dict(zip(headers, rows[0], strict=False))
