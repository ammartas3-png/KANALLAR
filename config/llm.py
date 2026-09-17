from __future__ import annotations

import json
from typing import Any, Literal

import httpx

from config.settings import get_settings

TaskTier = Literal["cheap", "normal", "premium"]


class LLMProvider:
    """Provider-agnostic router. Missing keys fall back to local callables."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def available(self) -> bool:
        return bool(self.settings.openai_api_key or self.settings.ollama_base_url)

    def complete(self, task: TaskTier, prompt: str, fallback: Any) -> tuple[Any, int, float]:
        """Return (parsed_or_text, tokens, cost). Tokens/cost are 0 on local fallback."""
        model = {
            "cheap": self.settings.llm_cheap_model,
            "normal": self.settings.llm_normal_model,
            "premium": self.settings.llm_premium_model,
        }[task]
        if self.settings.openai_api_key:
            try:
                text, tokens = self._openai(model, prompt)
                cost = tokens * (0.00015 / 1000)
                return self._maybe_json(text), tokens, cost
            except Exception:
                return fallback, 0, 0
        return fallback, 0, 0

    def _openai(self, model: str, prompt: str) -> tuple[str, int]:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
        }
        headers = {"Authorization": f"Bearer {self.settings.openai_api_key}"}
        response = httpx.post(
            f"{self.settings.openai_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=40,
        )
        response.raise_for_status()
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        tokens = int(data.get("usage", {}).get("total_tokens") or 0)
        return text, tokens

    @staticmethod
    def _maybe_json(text: str) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
