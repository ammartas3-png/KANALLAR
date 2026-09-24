"""Mark a row `video-hazir` as soon as its video renders.

Without this, a rendered row still reads `durum=beklemede` while Gate 2 or the
YouTube upload is pending, so the daily Schedule Trigger renders it again and
spends Kie credits a second time.

Usage: N8N_API_KEY=... python n8n/scripts/add_video_ready_status.py
"""

from __future__ import annotations

import copy
import json
import os
import re
import urllib.request
import uuid
from pathlib import Path

BASE = (os.environ.get("N8N_URL") or "https://ammartd20.app.n8n.cloud").rstrip("/")
WF_ID = "Xu72EtzVvMUHnBvO"
REPO_JSON = Path(__file__).resolve().parents[1] / "workflows/primary/youtube-full-pipeline.json"
H = {"X-N8N-API-KEY": os.environ["N8N_API_KEY"], "Content-Type": "application/json"}
SECRET_PATTERNS = [(r"apify_api_[A-Za-z0-9]+", ""), (r"954948d0865edad1015b65a269701d2b", ""), (r"kanallar-uretim-[0-9a-f]{32}", "kanallar-uretim-<secret>")]


def api(path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=H)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def main() -> None:
    w = api(f"/api/v1/workflows/{WF_ID}")
    nodes, conns = w["nodes"], w["connections"]
    nodes[:] = [n for n in nodes if n["name"] != "video-hazir-kayit"]
    conns.pop("video-hazir-kayit", None)
    N = {n["name"]: n for n in nodes}

    ready = copy.deepcopy(N["reddedildi"])
    vx, vy = N["video-bitti?"]["position"]
    ready.update({"id": str(uuid.uuid4()), "name": "video-hazir-kayit", "position": [vx + 100, vy - 320]})
    ready["parameters"]["columns"]["value"] = {"tarih": "={{ $('tarih-kontrol').item.json.tarih }}", "durum": "video-hazir"}
    nodes.append(ready)

    conns["video-bitti?"]["main"][0] = [{"node": "video-hazir-kayit", "type": "main", "index": 0}]
    conns["video-hazir-kayit"] = {"main": [[{"node": "video-gonder", "type": "main", "index": 0}]]}

    api(f"/api/v1/workflows/{WF_ID}", "PUT", {"name": w["name"], "nodes": nodes, "connections": conns, "settings": w["settings"]})
    live = api(f"/api/v1/workflows/{WF_ID}/activate", "POST", {})
    print("active:", live.get("active"), "nodes:", len(live["nodes"]))
    out = json.dumps({"name": live["name"], "nodes": live["nodes"], "connections": live["connections"], "settings": live.get("settings")},
                     indent=2, ensure_ascii=False)
    for pat, repl in SECRET_PATTERNS:
        out = re.sub(pat, repl, out)
    REPO_JSON.write_text(out)


if __name__ == "__main__":
    main()
