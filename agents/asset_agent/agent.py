from __future__ import annotations

from automation.logging import log_agent
from channels.loader import ChannelConfig
from config.settings import get_settings
from media.router import choose_scene_provider, status_report
from research.commons import search_images


@log_agent("AssetAgent")
def plan_assets(channel: ChannelConfig, script: dict, **kwargs) -> dict:
    """Hybrid plan: local FFmpeg cards by default; at most N Kie wow scenes."""
    settings = get_settings()
    quality = (kwargs.get("quality") or settings.media_quality or "hybrid").lower()
    max_kie = int(settings.max_kie_scenes_per_video)
    refs = search_images(script.get("topic") or channel.niche, limit=3)
    scenes = []
    kie_used = 0
    for scene in script["scenes"]:
        role = scene.get("role") or ""
        provider = choose_scene_provider(role, quality=quality)
        # Cap paid scenes even if multiple roles match wow
        if provider.name == "kie" and kie_used >= max_kie:
            provider = choose_scene_provider("body", quality="local")
        if provider.name == "kie":
            kie_used += 1
            decision = "kie_wow_planned"
            reason = f"Hybrid wow scene (role={role}); assembler may still use cards until async Kie fetch lands."
        elif provider.name == "higgsfield":
            decision = "higgsfield_planned"
            reason = "Premium provider selected."
        else:
            decision = "local_card"
            reason = "Hybrid default: zero-cost local card."
        scenes.append(
            {
                "role": role,
                "text": scene["text"],
                "decision": decision,
                "provider": provider.name,
                "reason": reason,
                "visual": scene.get("visual") or channel.niche,
                "prompt": scene.get("text") or script.get("hook") or "",
            }
        )
    engine = "local_cards" if kie_used == 0 else f"hybrid_kie_{kie_used}"
    return {
        "engine": engine,
        "media_quality": quality,
        "provider": "hybrid" if kie_used else "local",
        "kie_scenes": kie_used,
        "max_kie_scenes": max_kie,
        "providers": status_report(),
        "music": None,
        "sfx": [],
        "logo": True,
        "scenes": scenes,
        "commons_refs": refs,
        "token_usage": 0,
        "api_cost": 0,
    }
