from __future__ import annotations

from automation.logging import log_agent
from channels.loader import ChannelConfig
from config.settings import get_settings
from media.router import choose_provider, status_report
from research.commons import search_images


@log_agent("AssetAgent")
def plan_assets(channel: ChannelConfig, script: dict, **kwargs) -> dict:
    settings = get_settings()
    quality = kwargs.get("quality") or settings.media_quality
    provider = choose_provider("image", quality=quality)
    refs = search_images(script.get("topic") or channel.niche, limit=3)
    scenes = []
    for scene in script["scenes"]:
        if provider.name == "local":
            decision = "local_card"
            reason = "Ücretsiz yerel slayt; MediaProvider=local."
        else:
            decision = f"{provider.name}_planned"
            reason = (
                f"Sahne için {provider.name} seçildi (quality={quality}). "
                "Assembler V1 hâlâ FFmpeg kartları kullanır; AI clip indirme ayrı adım."
            )
        scenes.append(
            {
                "role": scene["role"],
                "text": scene["text"],
                "decision": decision,
                "provider": provider.name,
                "reason": reason,
                "visual": scene.get("visual") or channel.niche,
                "prompt": scene.get("text") or script.get("hook") or "",
            }
        )
    engine = "local_cards" if provider.name == "local" else f"hybrid_{provider.name}"
    return {
        "engine": engine,
        "media_quality": quality,
        "provider": provider.name,
        "providers": status_report(),
        "music": None,
        "sfx": [],
        "logo": True,
        "scenes": scenes,
        "commons_refs": refs,
        "token_usage": 0,
        "api_cost": 0,
    }
