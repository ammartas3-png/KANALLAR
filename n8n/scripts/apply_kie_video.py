"""Use Kie.ai Veo 3.1 for the video step of the PRIMARY workflow.

olustur        POST https://api.kie.ai/api/v1/veo/generate  (9:16, KIE_VIDEO_MODEL)
video-kontrol  GET  https://api.kie.ai/api/v1/veo/record-info?taskId=...
video-bitti?   successFlag == 1
video-tekrar?  successFlag == 0 and < 60 polls, else video-hata (with Kie message)
video-gonder   Telegram sendVideo by URL before Gate 2 (non-blocking)
indir          download resultUrls[0] as binary for the YouTube upload

The API key is written only to the live n8n workflow; the repo copy is scrubbed.

Usage: N8N_API_KEY=... KIE_API_KEY=... python n8n/scripts/apply_kie_video.py
"""

from __future__ import annotations

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
KIE_KEY = os.environ["KIE_API_KEY"]
KIE_VIDEO_MODEL = os.environ.get("KIE_VIDEO_MODEL", "veo3_fast")

RESULT_URL = "$('video-kontrol').item.json.data.response.resultUrls[0]"
CREATE_BODY = (
    "={{ JSON.stringify({ model: '" + KIE_VIDEO_MODEL + "', aspect_ratio: '9:16', enable_translation: true, prompt: (() => {"
    " const s = $json['sahne-prompt'];"
    " let p = s;"
    " try { const o = typeof s === 'string' ? JSON.parse(s) : s; p = o.prompt || s; } catch (e) {}"
    " return (String(p) + '\\n\\nVertical 9:16 YouTube Short. Any narration or on-screen text must be in the language of this title: ' + $json.baslik).slice(0, 4000);"
    " })() }) }}"
)


def api(path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=H)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def kie_headers() -> dict:
    return {"parameters": [{"name": "Authorization", "value": f"Bearer {KIE_KEY}"}, {"name": "accept", "value": "application/json"}]}


def scrub(text: str) -> str:
    text = re.sub(r"apify_api_[A-Za-z0-9]+", "", text)
    return text.replace(KIE_KEY, "")


def main() -> None:
    w = api(f"/api/v1/workflows/{WF_ID}")
    nodes, conns = w["nodes"], w["connections"]
    nodes[:] = [n for n in nodes if n["name"] != "video-gonder"]
    conns.pop("video-gonder", None)
    N = {n["name"]: n for n in nodes}

    N["olustur"]["parameters"] = {
        "method": "POST", "url": "https://api.kie.ai/api/v1/veo/generate",
        "sendHeaders": True, "headerParameters": kie_headers(),
        "sendBody": True, "specifyBody": "json", "jsonBody": CREATE_BODY, "options": {},
    }
    N["video-kontrol"]["parameters"] = {
        "url": "=https://api.kie.ai/api/v1/veo/record-info?taskId={{ $('olustur').item.json.data?.taskId }}",
        "sendHeaders": True, "headerParameters": kie_headers(), "options": {},
    }
    for name in ("olustur", "video-kontrol"):
        N[name].pop("credentials", None)

    def bool_cond(expr: str) -> dict:
        return {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                "conditions": [{"id": str(uuid.uuid4()), "leftValue": "={{ " + expr + " }}", "rightValue": "",
                                "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                "combinator": "and",
            },
            "options": {},
        }

    N["video-bitti?"]["parameters"] = bool_cond("$json.data?.successFlag === 1")
    N["video-tekrar?"]["parameters"] = bool_cond("$json.data?.successFlag === 0 && $runIndex < 60")
    N["video-hata"]["parameters"]["text"] = (
        "=Video uretimi durdu (Kie): flag={{ $json.data?.successFlag }} "
        "{{ $json.data?.errorMessage || $json.msg || '' }} | create: {{ $('olustur').item.json.msg }}"
    )

    vx, vy = N["video-bitti?"]["position"]
    nodes.append({
        "id": str(uuid.uuid4()), "name": "video-gonder", "type": "n8n-nodes-base.telegram", "typeVersion": 1.2,
        "position": [vx + 200, vy - 180], "webhookId": str(uuid.uuid4()),
        "parameters": {"operation": "sendVideo", "chatId": N["onay?"]["parameters"]["chatId"], "file": "={{ " + RESULT_URL + " }}",
                       "additionalFields": {"caption": "={{ $('tarih-kontrol').item.json.baslik }}"}},
        "credentials": N["onay?"]["credentials"],
        "onError": "continueRegularOutput",
    })
    conns["video-bitti?"] = {"main": [[{"node": "video-gonder", "type": "main", "index": 0}],
                                      [{"node": "video-tekrar?", "type": "main", "index": 0}]]}
    conns["video-gonder"] = {"main": [[{"node": "onay?", "type": "main", "index": 0}]]}

    N["onay?"]["parameters"]["message"] = (
        "=GATE 2 — Video hazır\nKanal: TAŞDEMiR MA (@tasdemirma3215)\n"
        "{{ $('tarih-kontrol').item.json.baslik }}\n{{ " + RESULT_URL + " }}"
    )

    N["indir"].update({"type": "n8n-nodes-base.httpRequest", "typeVersion": 4.3})
    N["indir"]["parameters"] = {
        "url": "={{ " + RESULT_URL + " }}",
        "options": {"response": {"response": {"responseFormat": "file", "outputPropertyName": "data"}}},
    }
    N["indir"].pop("credentials", None)

    api(f"/api/v1/workflows/{WF_ID}", "PUT", {"name": w["name"], "nodes": nodes, "connections": conns, "settings": w["settings"]})
    live = api(f"/api/v1/workflows/{WF_ID}/activate", "POST", {})
    print("active:", live.get("active"), "nodes:", len(live["nodes"]), "model:", KIE_VIDEO_MODEL)
    out = json.dumps({"name": live["name"], "nodes": live["nodes"], "connections": live["connections"], "settings": live.get("settings")},
                     indent=2, ensure_ascii=False)
    REPO_JSON.write_text(scrub(out))


if __name__ == "__main__":
    main()
