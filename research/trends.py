from __future__ import annotations

from datetime import datetime, timezone

import httpx


def wikipedia_most_read(language: str = "tr", limit: int = 8) -> list[dict]:
    """Free trend signal. No Google Trends key required."""
    day = datetime.now(timezone.utc).strftime("%Y/%m/%d")
    url = f"https://{language}.wikipedia.org/api/rest_v1/feed/featured/{day}"
    try:
        response = httpx.get(url, timeout=8, headers={"User-Agent": "Kanallar/0.2"})
        response.raise_for_status()
        articles = (((response.json() or {}).get("mostread") or {}).get("articles")) or []
    except Exception:
        return []
    rows = []
    for item in articles[:limit]:
        title = item.get("title") or item.get("normalizedtitle")
        if not title:
            continue
        rows.append(
            {
                "title": title.replace("_", " "),
                "views": item.get("views") or 0,
                "url": ((item.get("content_urls") or {}).get("desktop") or {}).get("page") or "",
                "source": "wikipedia_mostread",
            }
        )
    return rows
