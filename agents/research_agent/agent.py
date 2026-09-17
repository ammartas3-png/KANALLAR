from __future__ import annotations

import yaml

from automation.logging import log_agent
from channels.loader import ChannelConfig
from memory.store import used_topics
from research.wikipedia import summary
from research.ytdlp_meta import search_metadata


@log_agent("ResearchAgent")
def research(channel: ChannelConfig, topic_id: str | None = None, **kwargs) -> dict:
    catalog = yaml.safe_load(channel.catalog_path().read_text(encoding="utf-8")) or []
    used = used_topics(channel.id)
    unused = [item for item in catalog if item["id"] not in used]
    pool = unused or catalog
    chosen = next((item for item in pool if item["id"] == topic_id), None) if topic_id else pool[0]
    if chosen is None:
        raise KeyError(f"Konu yok: {topic_id}")

    wiki = summary(chosen["title"], channel.language)
    competitors = search_metadata(f"{chosen['title']} {channel.language} shorts", limit=3)
    hooks = [chosen["hook"]]
    if wiki.get("extract"):
        first = wiki["extract"].split(".")[0].strip()
        if first:
            hooks.append(first + ".")

    return {
        "topic": chosen["title"],
        "topic_id": chosen["id"],
        "reason": "Katalog + kullanılmamış konu; düşük maliyetli yerel araştırma.",
        "target_audience": "Meraklı yetişkin Shorts izleyicisi",
        "hook_ideas": hooks[:3],
        "estimated_potential": 0.72 if not used else 0.6,
        "source_urls": [wiki.get("url")] if wiki.get("url") else [],
        "competitor_examples": competitors,
        "catalog_item": chosen,
        "token_usage": 0,
        "api_cost": 0,
    }
