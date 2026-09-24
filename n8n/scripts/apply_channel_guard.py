"""Channel guard for the PRIMARY workflow (docs/CHANNELS_STATUS.md, rule 0 + G1.3/G1.4).

- `yayin-ayari` carries the target channel (HEDEF_KANAL_ID) and the blocked list.
- Before `Upload a video`: `kanal-dogrula` (YouTube channels mine) -> `kanal-kontrol`
  -> `kanal-ok?`. Upload only if the authorised channel id equals HEDEF_KANAL_ID and
  is not blocked; otherwise Telegram `kanal-engel` explains why. The binary from
  `indir` is re-attached so the upload still has the file.
- The personal-channel credential is removed from both YouTube nodes.
- The weekly research trigger is disabled until the target channel exists.

Usage: N8N_API_KEY=... python n8n/scripts/apply_channel_guard.py
Env: HEDEF_KANAL_ID, HEDEF_KANAL_ADI, YOUTUBE_CRED_ID, YOUTUBE_CRED_NAME, WEEKLY_ENABLED=1
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

BLOCKED_CHANNEL_IDS = ["UCa-ulc77JRueoWa11LPQUVg"]
PERSONAL_CREDENTIAL_IDS = {"Fhs1nwYca2mB8qu5"}
TARGET_ID = os.environ.get("HEDEF_KANAL_ID", "")
TARGET_NAME = os.environ.get("HEDEF_KANAL_ADI", "History in a Minute")
# Unauthorised placeholder: n8n refuses to publish YouTube nodes without a credential.
CRED_ID = os.environ.get("YOUTUBE_CRED_ID", "VE4bJp6Jb8KaVmII")
CRED_NAME = os.environ.get("YOUTUBE_CRED_NAME", "YouTube account")
WEEKLY_ENABLED = os.environ.get("WEEKLY_ENABLED") == "1"
SECRET_PATTERNS = [(r"apify_api_[A-Za-z0-9]+", ""), (r"954948d0865edad1015b65a269701d2b", ""),
                   (r"kanallar-uretim-[0-9a-f]{32}", "kanallar-uretim-<secret>")]


def api(path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=H)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path} -> {e.code}: {e.read()[:500].decode(errors='ignore')}")


def youtube_credentials() -> dict:
    if CRED_ID in PERSONAL_CREDENTIAL_IDS:
        raise SystemExit("refusing to wire the personal-channel credential")
    return {"youTubeOAuth2Api": {"id": CRED_ID, "name": CRED_NAME}}


def main() -> None:
    w = api(f"/api/v1/workflows/{WF_ID}")
    nodes, conns = w["nodes"], w["connections"]
    for old in ("kanal-dogrula", "kanal-kontrol", "kanal-ok?", "kanal-engel"):
        nodes[:] = [n for n in nodes if n["name"] != old]
        conns.pop(old, None)
    N = {n["name"]: n for n in nodes}
    creds = youtube_credentials()

    N["yayin-ayari"]["parameters"]["jsCode"] = (
        "return [{ json: { ...$json, YAYIN_ACIK: true, GIZLILIK: 'public', "
        f"HEDEF_KANAL_ID: {json.dumps(TARGET_ID)}, HEDEF_KANAL_ADI: {json.dumps(TARGET_NAME)}, "
        f"ENGELLI_KANALLAR: {json.dumps(BLOCKED_CHANNEL_IDS)} }}, pairedItem: {{ item: 0 }} }}];"
    )

    up = N["Upload a video"]
    ux, uy = up["position"]
    verify = {
        "id": str(uuid.uuid4()), "name": "kanal-dogrula", "type": "n8n-nodes-base.youTube", "typeVersion": 1,
        "position": [ux - 660, uy], "onError": "continueRegularOutput", "alwaysOutputData": True,
        "parameters": {"resource": "channel", "operation": "getAll", "returnAll": False, "limit": 1,
                       "part": ["snippet"], "filters": {"mine": True}, "options": {}},
    }
    check = {
        "id": str(uuid.uuid4()), "name": "kanal-kontrol", "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [ux - 440, uy],
        "parameters": {"jsCode": (
            "const cfg = $('yayin-ayari').first().json;\n"
            "const ch = $input.first().json;\n"
            "const id = ch.id || '';\n"
            "let sebep = '';\n"
            "if (!cfg.HEDEF_KANAL_ID) sebep = `hedef kanal (${cfg.HEDEF_KANAL_ADI}) henüz tanımlı değil`;\n"
            "else if (!id) sebep = `YouTube bağlantısı doğrulanamadı: ${ch.error || 'kanal yok'}`;\n"
            "else if (cfg.ENGELLI_KANALLAR.includes(id)) sebep = `ENGELLİ kanal (${ch.snippet?.title || id})`;\n"
            "else if (id !== cfg.HEDEF_KANAL_ID) sebep = `yanlış kanal: ${ch.snippet?.title || id}, beklenen ${cfg.HEDEF_KANAL_ADI}`;\n"
            "return [{ json: { kanal_ok: !sebep, sebep, kanal_id: id }, binary: $('indir').first().binary, pairedItem: { item: 0 } }];"
        )},
    }
    gate = {
        "id": str(uuid.uuid4()), "name": "kanal-ok?", "type": "n8n-nodes-base.if", "typeVersion": 2.3,
        "position": [ux - 220, uy],
        "parameters": {"conditions": {
            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
            "conditions": [{"id": str(uuid.uuid4()), "leftValue": "={{ $json.kanal_ok === true }}", "rightValue": "",
                            "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
            "combinator": "and"}, "options": {}},
    }
    blocked = {
        "id": str(uuid.uuid4()), "name": "kanal-engel", "type": "n8n-nodes-base.telegram", "typeVersion": 1.2,
        "position": [ux - 220, uy + 200], "webhookId": str(uuid.uuid4()),
        "parameters": {"chatId": N["onay?"]["parameters"]["chatId"],
                       "text": "=⛔ YouTube yüklemesi durduruldu: {{ $json.sebep }}\n{{ $('tarih-kontrol').item.json.baslik }}",
                       "additionalFields": {"appendAttribution": False}},
        "credentials": N["onay?"]["credentials"],
    }
    for node in (verify, up):
        node["credentials"] = creds
    nodes.extend([verify, check, gate, blocked])

    conns["DRY_RUN?"]["main"][0] = [{"node": "kanal-dogrula", "type": "main", "index": 0}]
    conns["kanal-dogrula"] = {"main": [[{"node": "kanal-kontrol", "type": "main", "index": 0}]]}
    conns["kanal-kontrol"] = {"main": [[{"node": "kanal-ok?", "type": "main", "index": 0}]]}
    conns["kanal-ok?"] = {"main": [[{"node": "Upload a video", "type": "main", "index": 0}],
                                   [{"node": "kanal-engel", "type": "main", "index": 0}]]}

    N["haftalik-tetik"]["disabled"] = not WEEKLY_ENABLED

    api(f"/api/v1/workflows/{WF_ID}", "PUT", {"name": w["name"], "nodes": nodes, "connections": conns, "settings": w["settings"]})
    live = api(f"/api/v1/workflows/{WF_ID}/activate", "POST", {})
    print("active:", live.get("active"), "target:", TARGET_ID or "(none)", "cred:", CRED_NAME or "(none)", "weekly:", WEEKLY_ENABLED)
    out = json.dumps({"name": live["name"], "nodes": live["nodes"], "connections": live["connections"], "settings": live.get("settings")},
                     indent=2, ensure_ascii=False)
    for pat, repl in SECRET_PATTERNS:
        out = re.sub(pat, repl, out)
    REPO_JSON.write_text(out)


if __name__ == "__main__":
    main()
