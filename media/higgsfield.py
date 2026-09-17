from __future__ import annotations

from typing import Any

import httpx

from config.settings import get_settings
from media.base import MediaJob


class HiggsfieldProvider:
    """Secondary / premium / fallback generative media provider."""

    name = "higgsfield"
    base_url = "https://platform.higgsfield.ai"

    def __init__(self) -> None:
        self.settings = get_settings()

    def configured(self) -> bool:
        return bool(self.settings.hf_api_key_id and self.settings.hf_api_key_secret)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": (
                f"Key {self.settings.hf_api_key_id}:{self.settings.hf_api_key_secret}"
            ),
            "Content-Type": "application/json",
        }

    def generate_image(self, prompt: str, **opts: Any) -> MediaJob:
        endpoint = opts.get("endpoint") or self.settings.hf_default_image_endpoint
        return self._submit(kind="image", endpoint=endpoint, body={"prompt": prompt, **opts.get("input", {})})

    def generate_video(self, prompt: str, **opts: Any) -> MediaJob:
        endpoint = opts.get("endpoint") or self.settings.hf_default_video_endpoint
        return self._submit(kind="video", endpoint=endpoint, body={"prompt": prompt, **opts.get("input", {})})

    def generate_voice(self, text: str, **opts: Any) -> MediaJob:
        endpoint = opts.get("endpoint") or self.settings.hf_default_voice_endpoint
        if not endpoint:
            return MediaJob(
                provider=self.name,
                external_id="",
                kind="voice",
                status="fail",
                error="HF voice endpoint tanımlı değil. docs.higgsfield.ai üzerinden doğrulayın.",
            )
        return self._submit(kind="voice", endpoint=endpoint, body={"text": text, **opts.get("input", {})})

    def get_job_status(self, job: MediaJob) -> MediaJob:
        if not self.configured():
            job.status = "not_configured"
            job.error = "HF_API_KEY_ID / HF_API_KEY_SECRET yok"
            return job
        status_url = job.raw.get("status_url") or f"{self.base_url}/requests/{job.external_id}/status"
        response = httpx.get(status_url, headers=self._headers(), timeout=60)
        response.raise_for_status()
        data = response.json()
        state = str(data.get("status") or "").lower()
        mapping = {
            "queued": "queued",
            "in_progress": "running",
            "running": "running",
            "completed": "success",
            "success": "success",
            "failed": "fail",
            "cancelled": "fail",
        }
        job.status = mapping.get(state, state or "running")
        job.raw = {**job.raw, **data}
        results = data.get("results") or data.get("images") or data.get("video") or []
        if isinstance(results, dict):
            for key in ("raw", "min", "url"):
                val = results.get(key)
                if isinstance(val, str):
                    job.result_urls = [val]
                elif isinstance(val, list):
                    job.result_urls = [str(x) for x in val]
        elif isinstance(results, list):
            job.result_urls = [str(x if isinstance(x, str) else x.get("url", "")) for x in results if x]
        if job.status == "fail":
            job.error = str(data.get("error") or data.get("message") or "Higgsfield failed")
        return job

    def estimate_cost(self, kind: str, **opts: Any) -> float:
        return float(opts.get("budget_hint") or 0)

    def _submit(self, kind: str, endpoint: str, body: dict[str, Any]) -> MediaJob:
        if not self.configured():
            return MediaJob(
                provider=self.name,
                external_id="",
                kind=kind,
                status="not_configured",
                error="HF_API_KEY_ID / HF_API_KEY_SECRET yok. Higgsfield Cloud'dan alın.",
            )
        if not endpoint:
            return MediaJob(
                provider=self.name,
                external_id="",
                kind=kind,
                status="fail",
                error="Endpoint boş. https://docs.higgsfield.ai üzerinden model endpoint seçin.",
            )
        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint.lstrip('/')}"
        response = httpx.post(url, headers=self._headers(), json=body, timeout=60)
        if response.status_code >= 400:
            return MediaJob(
                provider=self.name,
                external_id="",
                kind=kind,
                status="fail",
                model=endpoint,
                error=f"HTTP {response.status_code}: {response.text[:500]}",
            )
        data = response.json()
        request_id = str(data.get("request_id") or data.get("id") or "")
        return MediaJob(
            provider=self.name,
            external_id=request_id,
            kind=kind,
            status="queued" if request_id else "fail",
            model=endpoint,
            raw=data,
            error="" if request_id else "request_id dönmedi",
        )
