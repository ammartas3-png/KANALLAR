from __future__ import annotations

from automation.logging import log_agent
from channels.loader import ChannelConfig


@log_agent("AssetAgent")
def plan_assets(channel: ChannelConfig, script: dict, **kwargs) -> dict:
    scenes = []
    for scene in script["scenes"]:
        scenes.append(
            {
                "role": scene["role"],
                "text": scene["text"],
                "decision": "local_card",
                "reason": "Ücretsiz yerel slayt; AI video yok.",
                "visual": scene.get("visual") or channel.niche,
            }
        )
    return {
        "engine": "local_cards",
        "music": None,
        "sfx": [],
        "logo": True,
        "scenes": scenes,
        "token_usage": 0,
        "api_cost": 0,
    }
