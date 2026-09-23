"""Print the latest PRIMARY executions and the node trail of the newest one.

Usage: N8N_API_KEY=... python n8n/scripts/exec_status.py [execution_id]
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request

BASE = (os.environ.get("N8N_URL") or "https://ammartd20.app.n8n.cloud").rstrip("/")
H = {"X-N8N-API-KEY": os.environ["N8N_API_KEY"]}
WF_ID = "Xu72EtzVvMUHnBvO"


def get(path: str) -> dict:
    with urllib.request.urlopen(urllib.request.Request(f"{BASE}{path}", headers=H), timeout=60) as r:
        return json.loads(r.read())


def main() -> None:
    runs = get(f"/api/v1/executions?workflowId={WF_ID}&limit=3")["data"]
    for e in runs:
        print(e["id"], e["status"], e["startedAt"], "waitTill=", e.get("waitTill"))
    eid = sys.argv[1] if len(sys.argv) > 1 else runs[0]["id"]
    ex = get(f"/api/v1/executions/{eid}?includeData=true")
    res = (ex.get("data") or {}).get("resultData") or {}
    print(f"\n#{eid} status={ex.get('status')} lastNode={res.get('lastNodeExecuted')}")
    for name, node_runs in (res.get("runData") or {}).items():
        last = node_runs[-1]
        if last.get("error"):
            err = last["error"]
            print(f"  FAIL {name} x{len(node_runs)}: {err.get('message')} | {(err.get('description') or '')[:300]}")
        else:
            main_out = (last.get("data") or {}).get("main") or [[]]
            count = sum(len(b or []) for b in main_out)
            print(f"  ok   {name} x{len(node_runs)} items={count}")
    err = res.get("error")
    if err:
        print("ERROR:", err.get("message"), "|", (err.get("description") or "")[:400])


if __name__ == "__main__":
    main()
