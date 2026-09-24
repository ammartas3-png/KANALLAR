from __future__ import annotations

import yaml

from automation.logging import log_agent
from channels.loader import ChannelConfig
from memory.store import used_topics
from research.trends import wikipedia_most_read
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
    trends = wikipedia_most_read(channel.language)
    competitors = search_metadata(f"{chosen['title']} {channel.language} shorts", limit=3)
    hooks = [chosen["hook"]]
    if wiki.get("extract"):
        first = wiki["extract"].split(".")[0].strip()
        if first:
            hooks.append(first + ".")

    overlap = {row["title"].lower() for row in trends}
    potential = 0.8 if chosen["title"].lower() in overlap else (0.72 if unused else 0.6)
    sources = [wiki.get("url")] if wiki.get("url") else []
    sources.extend(row["url"] for row in trends[:3] if row.get("url"))

    return {
        "topic": chosen["title"],
        "topic_id": chosen["id"],
        "reason": "Katalog + Wikipedia özet + most-read trend; kullanılmamış konu öncelikli.",
        "target_audience": "Meraklı yetişkin Shorts izleyicisi",
        "hook_ideas": hooks[:3],
        "estimated_potential": potential,
        "source_urls": [url for url in sources if url],
        "competitor_examples": competitors,
        "trends": trends,
        "catalog_item": chosen,
        "token_usage": 0,
        "api_cost": 0,
    }
