from __future__ import annotations

from pathlib import Path
from typing import Any

from channels.loader import ChannelConfig
from config.paths import ROOT
from config.settings import get_settings

UPLOAD_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


class YouTubeConfigError(RuntimeError):
    pass


def _secrets() -> Path:
    path = Path(get_settings().youtube_client_secrets).expanduser()
    return path if path.is_absolute() else ROOT / path


def _token() -> Path:
    path = Path(get_settings().youtube_token).expanduser()
    return path if path.is_absolute() else ROOT / path


def credentials_status() -> dict[str, bool]:
    return {"client_secrets": _secrets().exists(), "token": _token().exists()}


def _client(readonly: bool = False):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    if not _secrets().exists():
        raise YouTubeConfigError("client_secret.json yok")
    creds = None
    if _token().exists():
        creds = Credentials.from_authorized_user_file(str(_token()), UPLOAD_SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if readonly:
            raise YouTubeConfigError("YouTube token yok")
        flow = InstalledAppFlow.from_client_secrets_file(str(_secrets()), UPLOAD_SCOPES)
        creds = flow.run_local_server(port=0, open_browser=False)
        _token().write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def upload_short(
    channel: ChannelConfig,
    script: dict[str, Any],
    video: Path,
    thumb: Path | None,
    publish_at: str | None = None,
    playlist_id: str | None = None,
) -> dict[str, str]:
    from googleapiclient.http import MediaFileUpload

    from youtube.playlists import add_to_playlist

    youtube = _client()
    status: dict[str, Any] = {
        "privacyStatus": channel.upload.privacy,
        "selfDeclaredMadeForKids": channel.upload.made_for_kids,
    }
    if publish_at:
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at
    body = {
        "snippet": {
            "title": script["title"][:100],
            "description": script["description"][:4900],
            "tags": script.get("tags", [])[:15],
            "categoryId": channel.upload.category_id,
            "defaultLanguage": channel.upload.default_language,
            "defaultAudioLanguage": channel.language,
        },
        "status": status,
    }
    media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response["id"]
    if thumb and thumb.exists():
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumb), mimetype="image/png"),
        ).execute()
    if playlist_id:
        add_to_playlist(video_id, playlist_id)
    return {"youtube_id": video_id, "youtube_url": f"https://youtu.be/{video_id}"}


def fetch_channel() -> dict:
    youtube = _client(readonly=True)
    data = youtube.channels().list(part="snippet,statistics", mine=True).execute()
    items = data.get("items") or []
    if not items:
        return {}
    item = items[0]
    stats = item.get("statistics") or {}
    return {
        "id": item.get("id") or "",
        "title": item.get("snippet", {}).get("title") or "",
        "subscribers": int(stats.get("subscriberCount") or 0),
        "views": int(stats.get("viewCount") or 0),
        "videos": int(stats.get("videoCount") or 0),
    }


def fetch_video_stats(youtube_video_id: str) -> dict:
    youtube = _client(readonly=True)
    data = youtube.videos().list(part="statistics,snippet", id=youtube_video_id).execute()
    items = data.get("items") or []
    if not items:
        return {}
    stats = items[0].get("statistics") or {}
    return {
        "views": int(stats.get("viewCount") or 0),
        "likes": int(stats.get("likeCount") or 0),
        "comments": int(stats.get("commentCount") or 0),
        "favorites": int(stats.get("favoriteCount") or 0),
    }
