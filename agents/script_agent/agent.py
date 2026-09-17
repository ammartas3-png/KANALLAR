from __future__ import annotations

from automation.logging import log_agent
from channels.loader import ChannelConfig


@log_agent("ScriptAgent")
def write_script(channel: ChannelConfig, idea: dict, **kwargs) -> dict:
    scenes = [{"role": "hook", "text": idea["hook"], "visual": idea.get("visual") or ""}]
    for index, fact in enumerate(idea.get("facts") or [], start=1):
        scenes.append({"role": "fact", "text": fact, "visual": idea.get("visual") or "", "index": index})
    if idea.get("closer"):
        scenes.append({"role": "closer", "text": idea["closer"], "visual": idea.get("visual") or ""})
    scenes.append({"role": "cta", "text": channel.cta, "visual": idea.get("visual") or ""})
    narration = " ".join(scene["text"] for scene in scenes)
    title = _title(idea)
    description = "\n".join(
        [
            channel.tagline,
            "",
            idea["topic"],
            narration,
            "",
            " ".join(f"#{tag.replace(' ', '')}" for tag in idea.get("tags") or []),
            "",
            channel.description_footer.strip(),
        ]
    )
    words = len(narration.split())
    estimated = max(18, min(45, int(words / 2.4)))
    return {
        "hook": idea["hook"],
        "scenes": scenes,
        "cta": channel.cta,
        "estimated_duration": estimated,
        "narration": narration,
        "title": title,
        "description": description,
        "tags": list(dict.fromkeys([*(idea.get("tags") or []), *channel.upload.tags])),
        "topic": idea["topic"],
        "topic_id": idea["topic_id"],
        "hook_type": idea.get("hook_type") or "fact",
        "token_usage": 0,
        "api_cost": 0,
    }


def _title(idea: dict) -> str:
    base = f"{idea['topic']}: {idea['hook']}"
    if len(base) > 90:
        base = idea["topic"]
    title = base if base.endswith("#shorts") else f"{base} #shorts"
    return title[:100]
