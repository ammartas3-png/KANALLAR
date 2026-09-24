from __future__ import annotations

from pathlib import Path

from automation.logging import log_agent
from channels.loader import ChannelConfig
from youtube.api import YouTubeConfigError, credentials_status, upload_short
from youtube.guard import ChannelGuardError


def _skipped(reason: str, status: str = "skipped") -> dict:
    return {"status": status, "reason": reason, "token_usage": 0, "api_cost": 0}


@log_agent("UploadAgent")
def publish(channel: ChannelConfig, script: dict, video: Path, thumb: Path | None, **kwargs) -> dict:
    if not channel.youtube_channel_id:
        return _skipped(f"{channel.name}: youtube_channel_id boş, upload kapalı (docs/CHANNELS_STATUS.md).")
    status = credentials_status(channel.id)
    if not status["client_secrets"]:
        return _skipped("YouTube OAuth yok. client_secret.json eklenince private yükleme açılır.")
    if not status["token"]:
        return _skipped(
            f"{channel.id} token yok. OAuth'ta ilgili Brand kanalı seçip tokens/{channel.id}.json oluşturun."
        )
    try:
        result = upload_short(
            channel,
            script,
            video,
            thumb,
            playlist_id=channel.upload.playlist_id or None,
        )
    except ChannelGuardError as exc:
        return _skipped(str(exc), status="blocked_channel")
    except YouTubeConfigError as exc:
        return _skipped(str(exc))
    return {**result, "status": "uploaded", "token_usage": 0, "api_cost": 0}
