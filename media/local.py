from __future__ import annotations

from typing import Any

from media.base import MediaJob


class LocalCardsProvider:
    """Zero-cost fallback used by current FFmpeg card pipeline."""

    name = "local"

    def configured(self) -> bool:
        return True

    def generate_image(self, prompt: str, **opts: Any) -> MediaJob:
        return MediaJob(
            provider=self.name,
            external_id="local-image",
            kind="image",
            status="success",
            model="pillow-cards",
            raw={"prompt": prompt, "note": "Rendered later by video.slides"},
        )

    def generate_video(self, prompt: str, **opts: Any) -> MediaJob:
        return MediaJob(
            provider=self.name,
            external_id="local-video",
            kind="video",
            status="success",
            model="ffmpeg-kenburns",
            raw={"prompt": prompt, "note": "Motion applied in compose_short"},
        )

    def generate_voice(self, text: str, **opts: Any) -> MediaJob:
        return MediaJob(
            provider=self.name,
            external_id="local-voice",
            kind="voice",
            status="success",
            model="edge-gtts-espeak",
            raw={"chars": len(text)},
        )

    def get_job_status(self, job: MediaJob) -> MediaJob:
        return job

    def estimate_cost(self, kind: str, **opts: Any) -> float:
        return 0.0
