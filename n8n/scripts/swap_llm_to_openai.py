"""Replace every Gemini chat-model sub-node in PRIMARY with an OpenAI chat model.

Gemini free tier allows only 20 requests/day per model, less than one research run
with retries. Chains, prompts and output parsers are untouched; only the model
sub-nodes (and their connection keys) change.

Usage: N8N_API_KEY=... python n8n/scripts/swap_llm_to_openai.py
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path

BASE = (os.environ.get("N8N_URL") or "https://ammartd20.app.n8n.cloud").rstrip("/")
WF_ID = "Xu72EtzVvMUHnBvO"
REPO_JSON = Path(__file__).resolve().parents[1] / "workflows/primary/youtube-full-pipeline.json"
H = {"X-N8N-API-KEY": os.environ["N8N_API_KEY"], "Content-Type": "application/json"}
MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
CRED = {"openAiApi": {"id": "jxy59ikFPZJ2RYDf", "name": "OpenAI account"}}
SECRET_PATTERNS = [r"apify_api_[A-Za-z0-9]+", r"954948d0865edad1015b65a269701d2b"]


def api(path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=H)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def main() -> None:
    w = api(f"/api/v1/workflows/{WF_ID}")
    nodes, conns = w["nodes"], w["connections"]
    renames: dict[str, str] = {}
    for n in nodes:
        if n["type"] != "@n8n/n8n-nodes-langchain.lmChatGoogleGemini":
            continue
        new_name = n["name"].replace("Google Gemini Chat Model", "OpenAI Chat Model")
        renames[n["name"]] = new_name
        n.update({
            "name": new_name,
            "type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
            "typeVersion": 1.2,
            "parameters": {"model": {"__rl": True, "mode": "list", "value": MODEL}, "options": {"temperature": 0.7}},
            "credentials": CRED,
            "retryOnFail": True,
            "maxTries": 3,
            "waitBetweenTries": 5000,
        })
    for old, new in renames.items():
        if old in conns:
            conns[new] = conns.pop(old)
    for n in nodes:
        if n.get("name") == "GEMINI MODEL":
            n["name"] = "LLM MODEL"
            n["parameters"]["content"] = (
                f"## LLM\nTum chat model node'lari: OpenAI `{MODEL}`\n"
                "Gemini ucretsiz katman: model basina gunde 20 istek (bir tur icin yetmiyor)."
            )

    api(f"/api/v1/workflows/{WF_ID}", "PUT", {"name": w["name"], "nodes": nodes, "connections": conns, "settings": w["settings"]})
    live = api(f"/api/v1/workflows/{WF_ID}/activate", "POST", {})
    print("active:", live.get("active"), "swapped:", len(renames), "model:", MODEL)
    out = json.dumps({"name": live["name"], "nodes": live["nodes"], "connections": live["connections"], "settings": live.get("settings")},
                     indent=2, ensure_ascii=False)
    for pat in SECRET_PATTERNS:
        out = re.sub(pat, "", out)
    REPO_JSON.write_text(out)


if __name__ == "__main__":
    main()
