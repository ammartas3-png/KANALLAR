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
                "local": "default hybrid scenes (zero $)",
                "kie": "wow/hook scenes only in hybrid mode",
                "higgsfield": "premium override / fallback",
            }.get(name, ""),
        }
    return report


def choose_provider(kind: str, quality: str = "hybrid") -> MediaProvider:
    """Pick provider for cost-aware hybrid factory.

    quality:
      local   — always cards
      hybrid  — prefer local; caller assigns kie only to wow roles
      cheap   — kie if configured else local
      auto    — same as hybrid (money-first default)
      premium — higgsfield if configured else kie else local
    """
    available = providers()
    q = (quality or "hybrid").lower()
    if q in {"local", "hybrid", "auto"}:
        # hybrid/auto: default path is local; scene planner may opt into kie per role
        if q == "local":
            return available["local"]
        return available["local"]
    if q == "premium" and available["higgsfield"].configured():
        return available["higgsfield"]
    if q in {"cheap", "premium"} and available["kie"].configured():
        return available["kie"]
    if available["higgsfield"].configured():
        return available["higgsfield"]
    return available["local"]


def choose_scene_provider(role: str, quality: str = "hybrid") -> MediaProvider:
    """Per-scene picker: only hook (and optionally cta) may use paid Kie in hybrid."""
    from config.settings import get_settings

    settings = get_settings()
    available = providers()
    q = (quality or settings.media_quality or "hybrid").lower()
    role_l = (role or "").lower()
    wow_roles = {"hook", "cta", "opener"}
    if q == "local":
        return available["local"]
    if q in {"hybrid", "auto"} and settings.kie_wow_roles_only:
        if role_l in wow_roles and available["kie"].configured():
            return available["kie"]
        return available["local"]
    return choose_provider("image", quality=q)


def generate(kind: str, prompt_or_text: str, quality: str = "hybrid", **opts) -> MediaJob:
    provider = choose_provider(kind, quality=quality)
    if kind == "image":
        return provider.generate_image(prompt_or_text, **opts)
    if kind == "video":
        return provider.generate_video(prompt_or_text, **opts)
    if kind == "voice":
        return provider.generate_voice(prompt_or_text, **opts)
    raise ValueError(f"Unknown media kind: {kind}")
