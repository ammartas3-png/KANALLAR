from __future__ import annotations

from typing import Any

from kanallar.catalog.loader import Topic
from kanallar.config import ChannelConfig


def build_script(channel: ChannelConfig, topic: Topic) -> dict[str, Any]:
    scenes = [{"role": "hook", "text": topic.hook, "visual": topic.visual}]
    for index, fact in enumerate(topic.facts, start=1):
        scenes.append(
            {
                "role": "fact",
                "text": fact,
                "visual": topic.visual,
                "index": index,
            }
        )
    if topic.closer:
        scenes.append({"role": "closer", "text": topic.closer, "visual": topic.visual})
    if channel.cta:
        scenes.append({"role": "cta", "text": channel.cta, "visual": topic.visual})

    narration = " ".join(scene["text"] for scene in scenes)
    title = _youtube_title(channel, topic)
    description = _description(channel, topic, narration)
    tags = list(dict.fromkeys([*topic.tags, *channel.upload.tags, channel.name.lower()]))
    return {
        "title": title,
        "topic_title": topic.title,
        "hook": topic.hook,
        "narration": narration,
        "scenes": scenes,
        "description": description,
        "tags": tags,
        "language": channel.language,
        "visual": topic.visual,
    }


def _youtube_title(channel: ChannelConfig, topic: Topic) -> str:
    base = f"{topic.title}: {topic.hook}"
    if len(base) > 96:
        base = topic.title
    suffix = " #shorts"
    title = base if base.endswith(suffix) else f"{base}{suffix}"
    return title[:100]


def _description(channel: ChannelConfig, topic: Topic, narration: str) -> str:
    lines = [
        channel.tagline,
        "",
        topic.title,
        narration,
        "",
        " ".join(f"#{tag.replace(' ', '')}" for tag in topic.tags),
        "",
        channel.description_footer.strip(),
    ]
    return "\n".join(lines).strip()
