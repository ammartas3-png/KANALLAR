from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from kanallar.paths import CATALOG_DIR


@dataclass(frozen=True)
class Topic:
    id: str
    title: str
    hook: str
    facts: list[str]
    closer: str
    tags: list[str] = field(default_factory=list)
    visual: str = ""


def load_catalog(name: str, catalog_dir: Path | None = None) -> list[Topic]:
    directory = catalog_dir or CATALOG_DIR
    path = directory / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Katalog bulunamadı: {name} ({path})")
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    topics = []
    for item in raw:
        topics.append(
            Topic(
                id=item["id"],
                title=item["title"],
                hook=item["hook"],
                facts=list(item.get("facts") or []),
                closer=item.get("closer") or "",
                tags=list(item.get("tags") or []),
                visual=item.get("visual") or "",
            )
        )
    return topics


def pick_topic(
    catalog_name: str,
    used_ids: set[str] | None = None,
    topic_id: str | None = None,
    catalog_dir: Path | None = None,
) -> Topic:
    topics = load_catalog(catalog_name, catalog_dir)
    if not topics:
        raise ValueError(f"Katalog boş: {catalog_name}")
    if topic_id:
        for topic in topics:
            if topic.id == topic_id:
                return topic
        raise KeyError(f"Konu bulunamadı: {topic_id}")
    unused = [topic for topic in topics if topic.id not in (used_ids or set())]
    pool = unused or topics
    return pool[0]
