from __future__ import annotations

from media.base import MediaJob, MediaProvider
from media.higgsfield import HiggsfieldProvider
from media.kie import KieProvider
from media.local import LocalCardsProvider


def providers() -> dict[str, MediaProvider]:
    return {
        "local": LocalCardsProvider(),
        "kie": KieProvider(),
        "higgsfield": HiggsfieldProvider(),
    }


def status_report() -> dict:
    report = {}
    for name, provider in providers().items():
        report[name] = {
            "configured": provider.configured(),
            "role": {
                "local": "zero-cost fallback (current produce path)",
                "kie": "primary AI media gateway",
                "higgsfield": "secondary/premium/fallback",
            }.get(name, ""),
        }
    return report


def choose_provider(kind: str, quality: str = "auto") -> MediaProvider:
    """Pick provider without forcing expensive models.

    quality: auto | local | cheap | premium
    """
    available = providers()
    if quality == "local":
        return available["local"]
    if quality == "premium" and available["higgsfield"].configured():
        return available["higgsfield"]
    if quality in {"auto", "cheap"} and available["kie"].configured():
        return available["kie"]
    if available["higgsfield"].configured():
        return available["higgsfield"]
    return available["local"]


def generate(kind: str, prompt_or_text: str, quality: str = "auto", **opts) -> MediaJob:
    provider = choose_provider(kind, quality=quality)
    if kind == "image":
        return provider.generate_image(prompt_or_text, **opts)
    if kind == "video":
        return provider.generate_video(prompt_or_text, **opts)
    if kind == "voice":
        return provider.generate_voice(prompt_or_text, **opts)
    raise ValueError(f"Unknown media kind: {kind}")
