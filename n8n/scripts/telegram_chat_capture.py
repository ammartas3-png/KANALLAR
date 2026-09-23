"""Temporary Telegram trigger that replies with the sender's chat id.

`start`  -> create + activate "TEMP telegram chat-id capture"
`read`   -> print chat ids seen so far
`stop`   -> deactivate + delete it

The n8n "Telegram account" bot's username is not readable through the API, so the
operator sends any message to the bot and this workflow reports the chat id.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import uuid

BASE = (os.environ.get("N8N_URL") or "https://ammartd20.app.n8n.cloud").rstrip("/")
H = {"X-N8N-API-KEY": os.environ["N8N_API_KEY"], "Content-Type": "application/json"}
NAME = "TEMP telegram chat-id capture"
CRED = {"telegramApi": {"id": "q14sD9Geek2ExOku", "name": "Telegram account"}}


def api(path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=H)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def find() -> dict | None:
    return next((w for w in api("/api/v1/workflows?limit=100")["data"] if w["name"] == NAME), None)


def start() -> None:
    if find():
        print("already running")
        return
    wf = {
        "name": NAME, "settings": {"executionOrder": "v1"},
        "nodes": [
            {"id": str(uuid.uuid4()), "name": "tg", "type": "n8n-nodes-base.telegramTrigger", "typeVersion": 1.2,
             "position": [0, 0], "webhookId": str(uuid.uuid4()), "parameters": {"updates": ["message"], "additionalFields": {}},
             "credentials": CRED},
            {"id": str(uuid.uuid4()), "name": "reply", "type": "n8n-nodes-base.telegram", "typeVersion": 1.2,
             "position": [240, 0], "webhookId": str(uuid.uuid4()),
             "parameters": {"chatId": "={{ $json.message.chat.id }}",
                            "text": "=KANALLAR bağlandı ✅ chat id: {{ $json.message.chat.id }}\nGate onayları bu sohbete gelecek.",
                            "additionalFields": {"appendAttribution": False}},
             "credentials": CRED},
        ],
        "connections": {"tg": {"main": [[{"node": "reply", "type": "main", "index": 0}]]}},
    }
    w = api("/api/v1/workflows", "POST", wf)
    api(f"/api/v1/workflows/{w['id']}/activate", "POST", {})
    print("capture active:", w["id"])


def read() -> None:
    w = find()
    if not w:
        print("not running")
        return
    for e in api(f"/api/v1/executions?workflowId={w['id']}&limit=20&includeData=true")["data"]:
        run = ((e.get("data") or {}).get("resultData") or {}).get("runData") or {}
        for item in (run.get("tg") or [{}])[0].get("data", {}).get("main", [[]])[0] or []:
            msg = item["json"].get("message", {})
            print("chat_id:", msg.get("chat", {}).get("id"), "from:", msg.get("from", {}).get("username"), "text:", msg.get("text"))


def stop() -> None:
    w = find()
    if w:
        api(f"/api/v1/workflows/{w['id']}/deactivate", "POST", {})
        api(f"/api/v1/workflows/{w['id']}", "DELETE")
    print("stopped")


if __name__ == "__main__":
    {"start": start, "read": read, "stop": stop}[sys.argv[1]]()
