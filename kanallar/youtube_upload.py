from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from kanallar.config import ChannelConfig
from kanallar.paths import ROOT

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeConfigError(RuntimeError):
    pass


def client_secrets_path() -> Path:
    raw = os.environ.get("YOUTUBE_CLIENT_SECRETS", "client_secret.json")
    path = Path(raw).expanduser()
    return path if path.is_absolute() else ROOT / path


def token_path() -> Path:
    raw = os.environ.get("YOUTUBE_TOKEN", "token.json")
    path = Path(raw).expanduser()
    return path if path.is_absolute() else ROOT / path


def credentials_status() -> dict[str, bool]:
    return {
        "client_secrets": client_secrets_path().exists(),
        "token": token_path().exists(),
    }


def upload_video(channel: ChannelConfig, script: dict[str, Any], video: Path, thumb: Path | None) -> dict[str, str]:
    secrets = client_secrets_path()
    if not secrets.exists():
        raise YouTubeConfigError(
            "YouTube OAuth dosyası yok. Google Cloud'da YouTube Data API v3 açıp "
            "masaüstü istemci JSON'unu client_secret.json olarak koyun."
        )

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = None
    saved = token_path()
    if saved.exists():
        creds = Credentials.from_authorized_user_file(str(saved), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(secrets), SCOPES)
        creds = flow.run_local_server(port=0, open_browser=False)
        saved.write_text(creds.to_json(), encoding="utf-8")

    youtube = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": script["title"][:100],
            "description": script["description"][:4900],
            "tags": script.get("tags", [])[:15],
            "categoryId": channel.upload.category_id,
            "defaultLanguage": channel.upload.default_language,
            "defaultAudioLanguage": channel.language,
        },
        "status": {
            "privacyStatus": channel.upload.privacy,
            "selfDeclaredMadeForKids": channel.upload.made_for_kids,
        },
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
    return {
        "youtube_id": video_id,
        "youtube_url": f"https://youtu.be/{video_id}",
    }
