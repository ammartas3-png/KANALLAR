from __future__ import annotations

from pathlib import Path

from automation.logging import log_agent
from channels.loader import ChannelConfig
from youtube.api import credentials_status, upload_short


@log_agent("UploadAgent")
def publish(channel: ChannelConfig, script: dict, video: Path, thumb: Path | None, **kwargs) -> dict:
    if not credentials_status()["client_secrets"]:
        return {
            "status": "skipped",
            "reason": "YouTube OAuth yok. client_secret.json eklenince private yükleme açılır.",
            "token_usage": 0,
            "api_cost": 0,
        }
    result = upload_short(
        channel,
        script,
        video,
        thumb,
        playlist_id=channel.upload.playlist_id or None,
    )
    return {**result, "status": "uploaded", "token_usage": 0, "api_cost": 0}
