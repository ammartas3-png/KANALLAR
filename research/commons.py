from __future__ import annotations

import httpx


def search_images(query: str, limit: int = 3) -> list[dict]:
    """Wikimedia Commons stills only. Attribution required. No video download."""
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}",
        "gsrnamespace": 6,
        "gsrlimit": max(1, min(limit, 8)),
        "prop": "imageinfo",
        "iiprop": "url|mime|extmetadata|size",
        "iiurlwidth": 1280,
    }
    try:
        response = httpx.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            timeout=10,
            headers={"User-Agent": "Kanallar/0.2 (educational shorts factory)"},
        )
        response.raise_for_status()
        pages = ((response.json() or {}).get("query") or {}).get("pages") or {}
    except Exception:
        return []
    rows = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        mime = info.get("mime") or ""
        if not mime.startswith("image/"):
            continue
        meta = info.get("extmetadata") or {}
        license_name = (meta.get("LicenseShortName") or {}).get("value") or ""
        artist = (meta.get("Artist") or {}).get("value") or ""
        rows.append(
            {
                "title": page.get("title") or "",
                "url": info.get("thumburl") or info.get("url") or "",
                "page": info.get("descriptionurl") or "",
                "license": license_name,
                "artist": artist,
                "source": "wikimedia_commons",
            }
        )
    return rows
