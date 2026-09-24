from __future__ import annotations

from typing import Any

import httpx

from config.settings import get_settings
from media.base import MediaJob


class KieProvider:
    """Primary AI media gateway. Models must be chosen from https://kie.ai/market."""

    name = "kie"
    base_url = "https://api.kie.ai"

    def __init__(self) -> None:
        self.settings = get_settings()

    def configured(self) -> bool:
        return bool(self.settings.kie_api_key)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.kie_api_key}",
            "Content-Type": "application/json",
        }

    def generate_image(self, prompt: str, **opts: Any) -> MediaJob:
        model = opts.get("model") or self.settings.kie_default_image_model
        return self._create_task(kind="image", model=model, input_payload={"prompt": prompt, **opts.get("input", {})})

    def generate_video(self, prompt: str, **opts: Any) -> MediaJob:
        model = opts.get("model") or self.settings.kie_default_video_model
        return self._create_task(kind="video", model=model, input_payload={"prompt": prompt, **opts.get("input", {})})

    def generate_voice(self, text: str, **opts: Any) -> MediaJob:
        model = opts.get("model") or self.settings.kie_default_voice_model
        payload = {"text": text, **opts.get("input", {})}
        return self._create_task(kind="voice", model=model, input_payload=payload)

    def get_job_status(self, job: MediaJob) -> MediaJob:
        if not self.configured():
            job.status = "not_configured"
            job.error = "KIE_API_KEY yok"
            return job
        response = httpx.get(
            f"{self.base_url}/api/v1/jobs/recordInfo",
            params={"taskId": job.external_id},
            headers=self._headers(),
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        body = data.get("data") or data
        state = str(body.get("state") or body.get("status") or "").lower()
        mapping = {
            "waiting": "queued",
            "queuing": "queued",
            "generating": "running",
            "success": "success",
            "fail": "fail",
            "failed": "fail",
        }
        job.status = mapping.get(state, state or "running")
        job.raw = body
        result = body.get("resultJson") or body.get("result") or {}
        if isinstance(result, str):
            import json

            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                result = {}
        urls = result.get("resultUrls") or result.get("result_urls") or []
        if isinstance(urls, list):
            job.result_urls = [str(u) for u in urls]
        if job.status == "fail":
            job.error = str(body.get("failMsg") or body.get("msg") or "Kie task failed")
        return job

    def estimate_cost(self, kind: str, **opts: Any) -> float:
        # Live pricing is on https://kie.ai/pricing — do not hard-code vendor rates.
        return float(opts.get("budget_hint") or 0)

    def _create_task(self, kind: str, model: str, input_payload: dict[str, Any]) -> MediaJob:
        if not self.configured():
            return MediaJob(
                provider=self.name,
                external_id="",
                kind=kind,
                status="not_configured",
                model=model,
                error="KIE_API_KEY yok. https://kie.ai/api-key",
            )
        if not model:
            return MediaJob(
                provider=self.name,
                external_id="",
                kind=kind,
                status="fail",
                error="Model boş. https://kie.ai/market üzerinden model id seçin.",
            )
        payload: dict[str, Any] = {"model": model, "input": input_payload}
        if self.settings.kie_callback_url:
            payload["callBackUrl"] = self.settings.kie_callback_url
        response = httpx.post(
            f"{self.base_url}/api/v1/jobs/createTask",
            headers=self._headers(),
            json=payload,
            timeout=60,
        )
        if response.status_code >= 400:
            return MediaJob(
                provider=self.name,
                external_id="",
                kind=kind,
                status="fail",
                model=model,
                error=f"HTTP {response.status_code}: {response.text[:500]}",
            )
        data = response.json()
        body = data.get("data") or data
        task_id = str(body.get("taskId") or body.get("task_id") or body.get("id") or "")
        return MediaJob(
            provider=self.name,
            external_id=task_id,
            kind=kind,
            status="queued" if task_id else "fail",
            model=model,
            raw=body,
            error="" if task_id else "taskId dönmedi",
        )
