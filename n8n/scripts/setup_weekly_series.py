"""Weekly series trigger + publish switch for the PRIMARY workflow.

- `haftalik-tetik` (Mon 10:00 Europe/Istanbul) -> `haftalik-girdi` -> `girdiler`
- `yayin-ayari` after `tarih`: single place to enable real uploads (Gate 2 PUBLISH still required)

Usage: N8N_API_KEY=... python n8n/scripts/setup_weekly_series.py
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
import uuid
from pathlib import Path

BASE = (os.environ.get("N8N_URL") or "https://ammartd20.app.n8n.cloud").rstrip("/")
KEY = os.environ["N8N_API_KEY"]
WF_ID = "Xu72EtzVvMUHnBvO"
REPO_JSON = Path(__file__).resolve().parents[1] / "workflows/primary/youtube-full-pipeline.json"
H = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}

SERIES_TOPIC = "Fatih Sultan Mehmed"
SERIES_LANG = "en"
PUBLISH_ENABLED = True
PRIVACY = "public"


def api(path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=H)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def main() -> None:
    w = api(f"/api/v1/workflows/{WF_ID}")
    nodes, conns = w["nodes"], w["connections"]
    for old in ("haftalik-tetik", "haftalik-girdi", "yayin-ayari"):
        nodes[:] = [n for n in nodes if n["name"] != old]
        conns.pop(old, None)
    N = {n["name"]: n for n in nodes}

    fx, fy = N["On form submission"]["position"]
    nodes.append({
        "id": str(uuid.uuid4()), "name": "haftalik-tetik", "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2, "position": [fx, fy - 200],
        "parameters": {"rule": {"interval": [{"field": "weeks", "weeksInterval": 1, "triggerAtDay": [1], "triggerAtHour": 10}]}},
    })
    nodes.append({
        "id": str(uuid.uuid4()), "name": "haftalik-girdi", "type": "n8n-nodes-base.code",
        "typeVersion": 2, "position": [fx + 220, fy - 200],
        "parameters": {"jsCode": f"return [{{ json: {{ 'Konu ': {json.dumps(SERIES_TOPIC)}, 'Hafta Sayısı': '1', 'İçerik Dili': {json.dumps(SERIES_LANG)} }} }}];"},
    })
    conns["haftalik-tetik"] = {"main": [[{"node": "haftalik-girdi", "type": "main", "index": 0}]]}
    conns["haftalik-girdi"] = {"main": [[{"node": "girdiler", "type": "main", "index": 0}]]}

    tx, ty = N["tarih"]["position"]
    nodes.append({
        "id": str(uuid.uuid4()), "name": "yayin-ayari", "type": "n8n-nodes-base.code",
        "typeVersion": 2, "position": [tx + 120, ty - 180],
        "parameters": {"jsCode": f"return [{{ json: {{ ...$json, YAYIN_ACIK: {str(PUBLISH_ENABLED).lower()}, GIZLILIK: {json.dumps(PRIVACY)} }}, pairedItem: {{ item: 0 }} }}];"},
    })
    conns["tarih"] = {"main": [[{"node": "yayin-ayari", "type": "main", "index": 0}]]}
    conns["yayin-ayari"] = {"main": [[{"node": "icerikler", "type": "main", "index": 0}]]}

    gate = N["DRY_RUN?"]["parameters"]["conditions"]
    gate["options"]["typeValidation"] = "loose"
    gate["conditions"] = [{
        "id": str(uuid.uuid4()),
        "leftValue": "={{ $('yayin-ayari').first().json.YAYIN_ACIK === true }}",
        "rightValue": "",
        "operator": {"type": "boolean", "operation": "true", "singleValue": True},
    }]
    N["DRY_RUN skip"]["parameters"]["text"] = "Upload atlandi (yayin-ayari: YAYIN_ACIK=false)."

    up = N["Upload a video"]["parameters"]
    up["categoryId"] = "27"
    up["regionCode"] = "US"
    up.setdefault("options", {})["privacyStatus"] = "={{ $('yayin-ayari').first().json.GIZLILIK }}"

    settings = w.get("settings") or {}
    settings["executionOrder"] = "v1"
    settings["timezone"] = "Europe/Istanbul"

    api(f"/api/v1/workflows/{WF_ID}", "PUT", {"name": w["name"], "nodes": nodes, "connections": conns, "settings": settings})
    live = api(f"/api/v1/workflows/{WF_ID}/activate", "POST", {})
    print("active:", live.get("active"), "nodes:", len(live["nodes"]))
    out = json.dumps({"name": live["name"], "nodes": live["nodes"], "connections": live["connections"], "settings": live.get("settings")},
                     indent=2, ensure_ascii=False)
    REPO_JSON.write_text(re.sub(r"apify_api_[A-Za-z0-9]+", "", out))


if __name__ == "__main__":
    main()
