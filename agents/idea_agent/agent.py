from __future__ import annotations

from automation.logging import log_agent
from channels.loader import ChannelConfig
from memory.store import profile


def _hook_type(hook: str) -> str:
    if "?" in hook:
        return "question"
    if any(char.isdigit() for char in hook):
        return "number"
    return "fact"


@log_agent("IdeaAgent")
def ideate(channel: ChannelConfig, brief: dict, **kwargs) -> dict:
    item = brief["catalog_item"]
    memory = profile(channel.id)
    winning = memory.get("winning_hooks", [])
    hook = item["hook"]
    if winning and "question" in " ".join(winning) and "?" not in hook:
        hook = f"{item['title']} neden önemli?"
    idea = {
        "topic": item["title"],
        "topic_id": item["id"],
        "hook": hook,
        "angle": item.get("visual") or channel.niche,
        "expected_duration": 28,
        "content_format": "shorts_explainer",
        "reason": brief.get("reason") or "Katalog gerçeği, tekrar yok.",
        "novelty_score": 0.85 if brief.get("estimated_potential") else 0.55,
        "hook_type": _hook_type(hook),
        "facts": item.get("facts") or [],
        "closer": item.get("closer") or "",
        "tags": item.get("tags") or [],
        "visual": item.get("visual") or "",
        "source": brief.get("source_urls") or [],
        "token_usage": 0,
        "api_cost": 0,
    }
    return idea
