from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from channels.loader import ChannelConfig
from config.paths import ROOT
from config.settings import get_settings
from youtube.guard import BLOCKED_CHANNEL_IDS, ChannelGuardError, assert_upload_allowed

log = logging.getLogger("kanallar.youtube")

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


def tokens_dir() -> Path:
    path = Path(get_settings().youtube_tokens_dir).expanduser()
    return path if path.is_absolute() else ROOT / path


def token_path(channel_key: str) -> Path:
    """One OAuth token per brand channel; the legacy single token.json is never read."""
    if not channel_key:
        raise YouTubeConfigError("kanal anahtarı boş")
    return tokens_dir() / f"{channel_key}.json"


def credentials_status(channel_key: str | None = None) -> dict[str, Any]:
    if channel_key:
        return {"client_secrets": _secrets().exists(), "token": token_path(channel_key).exists()}
    folder = tokens_dir()
    keys = sorted(p.stem for p in folder.glob("*.json")) if folder.exists() else []
    return {"client_secrets": _secrets().exists(), "token": bool(keys), "channel_tokens": keys}


def load_credentials(channel_key: str):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    path = token_path(channel_key)
    if not path.exists():
        raise YouTubeConfigError(f"{channel_key} için YouTube token yok ({path.name})")
    creds = Credentials.from_authorized_user_file(str(path), UPLOAD_SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        path.write_text(creds.to_json(), encoding="utf-8")
    if not creds.valid:
        raise YouTubeConfigError(f"{channel_key} token geçersiz; OAuth'u Brand kanalı seçerek yenileyin")
    return creds


def _client(channel_key: str):
    from googleapiclient.discovery import build

    return build("youtube", "v3", credentials=load_credentials(channel_key))


def authorised_channel_id(youtube) -> str:
    items = youtube.channels().list(part="id", mine=True).execute().get("items") or []
    return items[0]["id"] if items else ""


def verified_client(channel: ChannelConfig):
    """Client for writes; refuses unless the token belongs to channel.youtube_channel_id."""
    if not channel.youtube_channel_id:
        raise ChannelGuardError(f"{channel.id}: youtube_channel_id boş, upload kapalı")
    youtube = _client(channel.id)
    assert_upload_allowed(channel.youtube_channel_id, authorised_channel_id(youtube))
    return youtube


def next_publish_at(channel: ChannelConfig, now: datetime | None = None) -> str | None:
    """RFC3339 slot at channel.upload.schedule_hour (UTC) when scheduled publishing is enabled."""
    if not channel.upload.schedule_publish:
        return None
    now = now or datetime.now(timezone.utc)
    slot = now.replace(hour=channel.upload.schedule_hour, minute=0, second=0, microsecond=0)
    if slot <= now + timedelta(minutes=15):
        slot += timedelta(days=1)
    return slot.isoformat().replace("+00:00", "Z")


def build_upload_body(channel: ChannelConfig, script: dict[str, Any], publish_at: str | None) -> dict[str, Any]:
    status: dict[str, Any] = {
        "privacyStatus": channel.upload.privacy,
        "selfDeclaredMadeForKids": channel.upload.made_for_kids,
        "containsSyntheticMedia": True,
    }
    if publish_at:
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at
    tags = list(dict.fromkeys([*(script.get("tags") or []), *channel.upload.tags]))
    return {
        "snippet": {
            "title": script["title"][:100],
            "description": script["description"][:4900],
            "tags": tags[:15],
            "categoryId": channel.upload.category_id,
            "defaultLanguage": channel.upload.default_language,
            "defaultAudioLanguage": channel.language,
        },
        "status": status,
    }


def upload_short(
    channel: ChannelConfig,
    script: dict[str, Any],
    video: Path,
    thumb: Path | None,
    publish_at: str | None = None,
    playlist_id: str | None = None,
) -> dict[str, str]:
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    from youtube.playlists import add_to_playlist

    youtube = verified_client(channel)
    body = build_upload_body(channel, script, publish_at or next_publish_at(channel))
    media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()
    video_id = response["id"]
    result = {
        "youtube_id": video_id,
        "youtube_url": f"https://youtu.be/{video_id}",
        "publish_at": body["status"].get("publishAt", ""),
        "thumbnail_error": "",
        "playlist_error": "",
    }
    # Custom thumbnails need channel phone verification; until then YouTube answers 403
    # and the already-uploaded video must still be recorded.
    if thumb and thumb.exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumb), mimetype="image/png"),
            ).execute()
        except HttpError as exc:
            result["thumbnail_error"] = f"{exc.resp.status}: {exc.reason}"
            log.warning("thumbnail skipped for %s: %s", video_id, result["thumbnail_error"])
    if playlist_id:
        try:
            add_to_playlist(youtube, video_id, playlist_id)
        except HttpError as exc:
            result["playlist_error"] = f"{exc.resp.status}: {exc.reason}"
            log.warning("playlist add failed for %s: %s", video_id, result["playlist_error"])
    return result


def fetch_channel(channel_key: str) -> dict:
    youtube = _client(channel_key)
    data = youtube.channels().list(part="snippet,statistics", mine=True).execute()
    items = data.get("items") or []
    if not items:
        return {}
    item = items[0]
    if item.get("id") in BLOCKED_CHANNEL_IDS:
        raise ChannelGuardError(f"{channel_key} token engelli kanala ait")
    stats = item.get("statistics") or {}
    return {
        "id": item.get("id") or "",
        "title": item.get("snippet", {}).get("title") or "",
        "subscribers": int(stats.get("subscriberCount") or 0),
        "views": int(stats.get("viewCount") or 0),
        "videos": int(stats.get("videoCount") or 0),
    }


def fetch_video_stats(channel_key: str, youtube_video_id: str) -> dict:
    youtube = _client(channel_key)
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
