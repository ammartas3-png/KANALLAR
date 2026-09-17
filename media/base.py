from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class MediaJob:
    provider: str
    external_id: str
    kind: str  # image | video | voice
    status: str  # queued | running | success | fail | not_configured
    result_urls: list[str] = field(default_factory=list)
    cost: float = 0.0
    model: str = ""
    error: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


class MediaProvider(Protocol):
    name: str

    def configured(self) -> bool: ...

    def generate_image(self, prompt: str, **opts: Any) -> MediaJob: ...

    def generate_video(self, prompt: str, **opts: Any) -> MediaJob: ...

    def generate_voice(self, text: str, **opts: Any) -> MediaJob: ...

    def get_job_status(self, job: MediaJob) -> MediaJob: ...

    def estimate_cost(self, kind: str, **opts: Any) -> float: ...
