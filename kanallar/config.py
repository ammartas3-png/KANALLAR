from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from kanallar.paths import CHANNELS_DIR


class Brand(BaseModel):
    primary: str = "#0A0E17"
    accent: str = "#F4B942"
    text: str = "#F4F1E8"
    muted: str = "#9AA3B5"


class UploadSettings(BaseModel):
    privacy: str = "private"
    category_id: str = "22"
    made_for_kids: bool = False
    default_language: str = "tr"
    tags: list[str] = Field(default_factory=list)


class ChannelConfig(BaseModel):
    id: str
    name: str
    tagline: str
    language: str = "tr"
    niche: str = "science"
    format: str = "shorts"
    voice: str = "tr-TR-AhmetNeural"
    voice_rate: str = "+0%"
    catalog: str = "science_tr"
    cta: str = ""
    description_footer: str = ""
    brand: Brand = Field(default_factory=Brand)
    upload: UploadSettings = Field(default_factory=UploadSettings)

    @property
    def is_shorts(self) -> bool:
        return self.format == "shorts"

    @property
    def video_size(self) -> tuple[int, int]:
        return (1080, 1920) if self.is_shorts else (1920, 1080)


def load_channel(channel_id: str, channels_dir: Path | None = None) -> ChannelConfig:
    directory = channels_dir or CHANNELS_DIR
    path = directory / f"{channel_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Kanal bulunamadı: {channel_id} ({path})")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ChannelConfig.model_validate(data)


def list_channels(channels_dir: Path | None = None) -> list[ChannelConfig]:
    directory = channels_dir or CHANNELS_DIR
    if not directory.exists():
        return []
    channels = [
        load_channel(path.stem, directory)
        for path in sorted(directory.glob("*.yaml"))
    ]
    return channels
