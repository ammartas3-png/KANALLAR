from __future__ import annotations

from automation.logging import log_agent
from channels.loader import ChannelConfig
from research.commons import search_images


@log_agent("AssetAgent")
def plan_assets(channel: ChannelConfig, script: dict, **kwargs) -> dict:
    refs = search_images(script.get("topic") or channel.niche, limit=3)
    scenes = []
    for scene in script["scenes"]:
        scenes.append(
            {
                "role": scene["role"],
                "text": scene["text"],
                "decision": "local_card",
                "reason": "Ücretsiz yerel slayt; Commons yalnızca referans/attribution.",
                "visual": scene.get("visual") or channel.niche,
            }
        )
    return {
        "engine": "local_cards",
        "music": None,
        "sfx": [],
        "logo": True,
        "scenes": scenes,
        "commons_refs": refs,
        "token_usage": 0,
        "api_cost": 0,
    }
