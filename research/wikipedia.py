from __future__ import annotations

import httpx


def summary(title: str, language: str = "tr") -> dict[str, str]:
    url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        response = httpx.get(url, timeout=8, follow_redirects=True, headers={"User-Agent": "Kanallar/0.1"})
        if response.status_code >= 400:
            return {}
        data = response.json()
        extract = (data.get("extract") or "").strip()
        if not extract:
            return {}
        return {
            "title": data.get("title") or title,
            "extract": extract[:600],
            "url": data.get("content_urls", {}).get("desktop", {}).get("page") or url,
            "source": "wikipedia",
        }
    except Exception:
        return {}
