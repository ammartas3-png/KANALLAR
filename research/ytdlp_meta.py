from __future__ import annotations

import json
import shutil
import subprocess


def search_metadata(query: str, limit: int = 5) -> list[dict]:
    """Metadata only. Never downloads media. Research/reference use."""
    binary = shutil.which("yt-dlp")
    if not binary:
        return []
    cmd = [
        binary,
        f"ytsearch{limit}:{query}",
        "--flat-playlist",
        "--dump-json",
        "--skip-download",
        "--no-warnings",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25, check=False)
    except Exception:
        return []
    rows = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        rows.append(
            {
                "title": item.get("title") or "",
                "url": item.get("url") or item.get("webpage_url") or "",
                "duration": item.get("duration"),
                "channel": item.get("channel") or item.get("uploader") or "",
            }
        )
    return rows
