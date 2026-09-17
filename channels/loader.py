from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from config.paths import CHANNELS_DIR
from config.settings import get_settings


class Brand(BaseModel):
    primary: str = "#0A0E17"
    accent: str = "#F4B942"
    text: str = "#F4F1E8"
    muted: str = "#9AA3B5"


class UploadRules(BaseModel):
    privacy: str = "private"
    category_id: str = "28"
    made_for_kids: bool = False
    default_language: str = "tr"
    tags: list[str] = Field(default_factory=list)
    frequency_per_day: int = 1
    schedule_hour: int = 20


class VoiceProfile(BaseModel):
    provider: str = "auto"
    voice: str = "tr-TR-AhmetNeural"
    rate: str = "+4%"
    language: str = "tr"


class ChannelConfig(BaseModel):
    id: str
    name: str
    tagline: str
    youtube_channel_id: str = ""
    niche: str = "science"
    language: str = "tr"
    country: str = "TR"
    format: str = "shorts"
    catalog: str = "catalog.yaml"
    prompt: str = ""
    cta: str = ""
    description_footer: str = ""
    brand: Brand = Field(default_factory=Brand)
    voice: VoiceProfile = Field(default_factory=VoiceProfile)
    upload: UploadRules = Field(default_factory=UploadRules)

    @property
    def video_size(self) -> tuple[int, int]:
        return (1080, 1920)

    def catalog_path(self, root: Path | None = None) -> Path:
        base = (root or CHANNELS_DIR) / self.id
        return base / self.catalog


def load_channel(channel_id: str | None = None, root: Path | None = None) -> ChannelConfig:
    channel_id = channel_id or get_settings().active_channel
    directory = (root or CHANNELS_DIR) / channel_id
    path = directory / "config.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Kanal yok: {channel_id}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ChannelConfig.model_validate(data)


def list_mvp_channel() -> ChannelConfig:
    return load_channel()
