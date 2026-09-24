from __future__ import annotations

from pathlib import Path

from automation.logging import log_agent
from channels.loader import ChannelConfig
from voice.provider import synthesize


@log_agent("VoiceAgent")
def narrate(channel: ChannelConfig, script: dict, work: Path, **kwargs) -> dict:
    audio = work / "narration.mp3"
    engine = synthesize(script["narration"], audio, channel)
    return {
        "audio": str(audio),
        "engine": engine,
        "provider": engine,
        "token_usage": 0,
        "api_cost": 0.0 if engine != "elevenlabs" else 0.02,
    }
