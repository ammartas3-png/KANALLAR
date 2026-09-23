"""Apply review-driven updates to the live PRIMARY workflow.

- Gate 1: 3 candidate Shorts -> Telegram form (1/2/3/new/cancel)
- Gate 2: PUBLISH / REVISE / REJECT + feedback, max 3 revisions
- Bounded polling for Apify and video jobs, failure notices
- Idempotency: only rows with durum=beklemede are produced; final status written back

Usage: N8N_API_KEY=... python n8n/scripts/apply_review_updates.py
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
KEY = os.environ["N8N_API_KEY"]
WF_ID = "Xu72EtzVvMUHnBvO"
CHAT = "8715342169"
REPO_JSON = Path(__file__).resolve().parents[1] / "workflows/primary/youtube-full-pipeline.json"
H = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}

MONTHS = "['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']"
TODAY_JS = (
    f"const aylar = {MONTHS};\n"
    "const t = new Date(Date.now() + 3 * 3600 * 1000);\n"
    "const bugun = `${t.getUTCDate()} ${aylar[t.getUTCMonth()]} ${t.getUTCFullYear()}`;\n"
)


def api(path: str, method: str = "GET", body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method, headers=H)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def cid() -> str:
    return str(uuid.uuid4())


def bool_if(name: str, expr: str, pos: list[int]) -> dict:
    return {
        "id": cid(),
        "name": name,
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.3,
        "position": pos,
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                "conditions": [
                    {
                        "id": cid(),
                        "leftValue": "={{ " + expr + " }}",
                        "rightValue": "",
                        "operator": {"type": "boolean", "operation": "true", "singleValue": True},
                    }
                ],
                "combinator": "and",
            },
            "options": {},
        },
    }


def code(name: str, js: str, pos: list[int], each: bool = False) -> dict:
    params = {"jsCode": js}
    if each:
        params["mode"] = "runOnceForEachItem"
    return {"id": cid(), "name": name, "type": "n8n-nodes-base.code", "typeVersion": 2, "position": pos, "parameters": params}


def tg_send(name: str, text: str, pos: list[int], cred: dict) -> dict:
    return {
        "id": cid(),
        "name": name,
        "type": "n8n-nodes-base.telegram",
        "typeVersion": 1.2,
        "position": pos,
        "webhookId": cid(),
        "parameters": {"chatId": CHAT, "text": text, "additionalFields": {"appendAttribution": False}},
        "credentials": cred,
    }


def tg_form(name: str, message: str, fields: list[dict], pos: list[int], cred: dict) -> dict:
    return {
        "id": cid(),
        "name": name,
        "type": "n8n-nodes-base.telegram",
        "typeVersion": 1.2,
        "position": pos,
        "webhookId": cid(),
        "parameters": {
            "operation": "sendAndWait",
            "chatId": CHAT,
            "message": message,
            "responseType": "customForm",
            "formFields": {"values": fields},
            "options": {},
        },
        "credentials": cred,
    }


def dropdown(label: str, options: list[str]) -> dict:
    return {
        "fieldLabel": label,
        "fieldType": "dropdown",
        "fieldOptions": {"values": [{"option": o} for o in options]},
        "requiredField": True,
    }


def status_writer(template: dict, name: str, durum: str, pos: list[int]) -> dict:
    node = copy.deepcopy(template)
    node["id"] = cid()
    node["name"] = name
    node["position"] = pos
    node["parameters"]["columns"]["value"] = {
        "tarih": "={{ $('tarih-kontrol').item.json.tarih }}",
        "durum": durum,
    }
    return node


def link(conns: dict, src: str, branches: list[list[str]]) -> None:
    conns[src] = {"main": [[{"node": t, "type": "main", "index": 0} for t in b] for b in branches]}


def main() -> None:
    w = api(f"/api/v1/workflows/{WF_ID}")
    nodes: list[dict] = w["nodes"]
    conns: dict = w["connections"]
    N = {n["name"]: n for n in nodes}
    tg_cred = N["onay?"]["credentials"]

    for old in ("onay-bekle", "If2", "Get row(s) in sheet2", "yeni-video-onay", "If3"):
        if old in N:
            nodes.remove(N.pop(old))
            conns.pop(old, None)
    for src in list(conns):
        for branches in conns[src].values():
            for b in branches:
                b[:] = [t for t in (b or []) if t["node"] in N or t["node"] in conns]

    # --- Gate 1: candidate topics ---
    plan = N["icerik-fikir-baslik-aciklama"]["parameters"]
    plan["text"] = re.sub(r"Uzun format sayısı:.*\n", "Uzun format sayısı: 0\n", plan["text"])
    plan["text"] = re.sub(r"Shorts sayısı:.*\n", "Shorts sayısı: 3\n", plan["text"])
    plan["text"] = re.sub(r"NOT: .*$", "NOT: Bunlar 3 farklı ADAY konudur; kullanıcı birini seçecek. Her biri farklı açı ve güçlü hook içersin.", plan["text"])

    ix, iy = N["icerik"]["position"]
    adaylar = code(
        "adaylar",
        "const items = $input.all().map(i => i.json);\n"
        "const metin = items.map((a, i) => `${i + 1}) ${a.baslik}\\n${a.aciklama}\\n${String(a['ana-tema'] || '').slice(0, 160)}…`).join('\\n\\n');\n"
        "return [{ json: { adaylar: items, metin } }];",
        [ix + 200, iy - 160],
    )
    konu_sec = tg_form(
        "konu-sec",
        "=GATE 1 — Konu seç\n\n{{ $json.metin }}",
        [dropdown("Secim", ["1", "2", "3", "Yeni fikirler", "Iptal"]), {"fieldLabel": "Not", "fieldType": "textarea"}],
        [ix + 420, iy - 160],
        tg_cred,
    )
    secilen = code(
        "secilen-konu",
        TODAY_JS
        + "const d = $json.data || $json;\n"
        "const secim = String(d.Secim ?? d.secim ?? '').trim();\n"
        "const adaylar = $('adaylar').first().json.adaylar;\n"
        "if (['1', '2', '3'].includes(secim)) {\n"
        "  const a = adaylar[Number(secim) - 1];\n"
        "  return [{ json: { ...a, format: 'short', tarih: bugun, aksiyon: 'sec' }, pairedItem: { item: 0 } }];\n"
        "}\n"
        "if (secim === 'Yeni fikirler') {\n"
        "  if ($runIndex >= 2) return [{ json: { aksiyon: 'iptal', sebep: 'yeni fikir limiti' }, pairedItem: { item: 0 } }];\n"
        "  return [{ json: { ...$('Aggregate').first().json, aksiyon: 'yeni' }, pairedItem: { item: 0 } }];\n"
        "}\n"
        "return [{ json: { aksiyon: 'iptal', sebep: 'kullanici iptal' }, pairedItem: { item: 0 } }];",
        [ix + 640, iy - 160],
    )
    secildi = bool_if("secildi?", "$json.aksiyon === 'sec'", [ix + 860, iy - 160])
    yeni = bool_if("yeni-fikir?", "$json.aksiyon === 'yeni'", [ix + 1060, iy])
    iptal = tg_send("konu-iptal", "=Gate 1 iptal: {{ $json.sebep }}", [ix + 1260, iy + 120], tg_cred)

    link(conns, "icerik", [["adaylar"]])
    link(conns, "adaylar", [["konu-sec"]])
    link(conns, "konu-sec", [["secilen-konu"]])
    link(conns, "secilen-konu", [["secildi?"]])
    link(conns, "secildi?", [["icerik-kayit"], ["yeni-fikir?"]])
    link(conns, "yeni-fikir?", [["icerik-fikir-baslik-aciklama"], ["konu-iptal"]])

    # Scene loop done -> mark only the selected row approved
    N["onaylandi"]["parameters"]["columns"]["value"] = {
        "tarih": "={{ $('secilen-konu').first().json.tarih }}",
        "durum": "beklemede",
    }
    loop = conns["Loop Over Items1"]["main"]
    loop[0] = [{"node": "onaylandi", "type": "main", "index": 0}]

    # Idempotency: produce only approved rows for today
    tk = N["tarih-kontrol"]["parameters"]["conditions"]
    tk["conditions"] = [c for c in tk["conditions"] if "durum" not in str(c.get("leftValue"))]
    tk["conditions"].append(
        {"id": cid(), "leftValue": "={{ $json.durum }}", "rightValue": "beklemede", "operator": {"type": "string", "operation": "equals"}}
    )

    # SEO per row
    seo = N["SEO preflight"]["parameters"]
    seo["mode"] = "runOnceForEachItem"
    seo["jsCode"] = (
        "const row = $json;\n"
        "const title = String(row.baslik || '').trim();\n"
        "const desc = String(row.aciklama || '').trim();\n"
        "const maxTitle = String(row.fomat || row.format || 'short').includes('long') ? 60 : 40;\n"
        "const issues = [];\n"
        "if (!title) issues.push('baslik bos'); else if (title.length > maxTitle) issues.push(`baslik ${title.length}>${maxTitle}`);\n"
        "if (!desc) issues.push('aciklama bos'); else if (desc.length < 20) issues.push('aciklama cok kisa');\n"
        "if (!row['sahne-prompt']) issues.push('sahne-prompt bos');\n"
        "return { json: { ...row, seo_ok: issues.length === 0, seo_issues: issues.join('; ') || 'ok' } };"
    )

    # --- Bounded polling ---
    N["Wait1"]["parameters"] = {"amount": 20, "unit": "seconds"}
    N["Wait"]["parameters"] = {"amount": 30, "unit": "seconds"}
    ax, ay = N["If1"]["position"]
    apify_retry = bool_if("apify-tekrar?", "['READY','RUNNING'].includes($json.data.status) && $runIndex < 45", [ax + 20, ay + 200])
    apify_fail = tg_send("apify-hata", "=Apify durdu: {{ $json.data.status }} (deneme {{ $runIndex + 1 }})", [ax + 240, ay + 360], tg_cred)
    link(conns, "If1", [["sonuc"], ["apify-tekrar?"]])
    link(conns, "apify-tekrar?", [["Wait1"], ["apify-hata"]])

    vx, vy = N["video-bitti?"]["position"]
    video_retry = bool_if(
        "video-tekrar?",
        "!['failed','error','cancelled','canceled'].includes(String($json.status).toLowerCase()) && $runIndex < 60",
        [vx + 20, vy + 200],
    )
    video_fail = tg_send("video-hata", "=Video uretimi durdu: {{ $json.status }}", [vx + 240, vy + 360], tg_cred)
    link(conns, "video-bitti?", [["onay?"], ["video-tekrar?"]])
    link(conns, "video-tekrar?", [["Wait"], ["video-hata"]])

    # --- Gate 2: PUBLISH / REVISE / REJECT ---
    gate2 = N["onay?"]
    gate2["parameters"] = {
        "operation": "sendAndWait",
        "chatId": CHAT,
        "message": "=GATE 2 — Video hazır\n{{ $('tarih-kontrol').item.json.baslik }}\n{{ $json.final_video_url }}",
        "responseType": "customForm",
        "formFields": {
            "values": [
                dropdown("Karar", ["PUBLISH", "REVISE", "REJECT"]),
                {"fieldLabel": "Geri bildirim", "fieldType": "textarea"},
            ]
        },
        "options": {},
    }
    gx, gy = N["video-onay?"]["position"]
    karar = code(
        "karar",
        "const d = $json.data || $json;\n"
        "return [{ json: { karar: String(d.Karar ?? d.karar ?? 'REJECT').toUpperCase(), geri_bildirim: String(d['Geri bildirim'] ?? '') }, pairedItem: { item: 0 } }];",
        [gx - 40, gy],
    )
    N["video-onay?"]["parameters"] = bool_if("x", "$json.karar === 'PUBLISH'", [0, 0])["parameters"]
    N["video-onay?"]["position"] = [gx + 180, gy]
    revize_mi = bool_if("revize?", "$json.karar === 'REVISE'", [gx + 180, gy + 220])
    revize = code(
        "revize-prompt",
        "if ($runIndex >= 3) throw new Error('Revizyon limiti (3) doldu');\n"
        "const row = $('tarih-kontrol').item.json;\n"
        "const fb = $json.geri_bildirim.trim();\n"
        "let body = row['sahne-prompt'];\n"
        "try {\n"
        "  const obj = typeof body === 'string' ? JSON.parse(body) : { ...body };\n"
        "  if (fb) obj.prompt = `${obj.prompt || ''}\\n\\nREVIZYON: ${fb}`;\n"
        "  body = JSON.stringify(obj);\n"
        "} catch (e) {}\n"
        "return [{ json: { ...row, 'sahne-prompt': body }, pairedItem: { item: 0 } }];",
        [gx + 400, gy + 220],
    )
    tmpl = N["onaylandi"]
    reddedildi = status_writer(tmpl, "reddedildi", "reddedildi", [gx + 400, gy + 420])
    yayinlandi = status_writer(tmpl, "yayinlandi", "yayinlandi", [N["Upload a video"]["position"][0] + 220, N["Upload a video"]["position"][1]])
    dry = N["DRY_RUN skip"]["position"]
    dryrun_kayit = status_writer(tmpl, "dry-run-kayit", "dry-run", [dry[0] + 220, dry[1]])

    link(conns, "onay?", [["karar"]])
    link(conns, "karar", [["video-onay?"]])
    link(conns, "video-onay?", [["indir"], ["revize?"]])
    link(conns, "revize?", [["revize-prompt"], ["reddedildi"]])
    link(conns, "revize-prompt", [["olustur"]])
    link(conns, "Upload a video", [["yayinlandi"]])
    link(conns, "DRY_RUN skip", [["dry-run-kayit"]])

    for n in nodes:
        if n["name"] == "OVERVIEW":
            n["parameters"]["content"] = (
                "## PRIMARY YouTube Full\n\n"
                "Form → araştırma → 3 aday → **Gate 1 seç** → sahne → Sheets `beklemede`\n"
                "→ SEO → video (max 30 dk) → **Gate 2 PUBLISH/REVISE/REJECT**\n"
                "→ DRY_RUN+AUTO_PUBLISH → YouTube → Sheets `yayinlandi`"
            )

    for n in (adaylar, konu_sec, secilen, secildi, yeni, iptal, apify_retry, apify_fail, video_retry, video_fail,
              karar, revize_mi, revize, reddedildi, yayinlandi, dryrun_kayit):
        nodes.append(n)

    names = {n["name"] for n in nodes}
    for src, outs in conns.items():
        assert src in names, f"dangling source {src}"
        for b in outs.get("main", []):
            for t in b or []:
                assert t["node"] in names, f"dangling target {src}->{t['node']}"

    body = {"name": w["name"], "nodes": nodes, "connections": conns, "settings": w.get("settings") or {"executionOrder": "v1"}}
    api(f"/api/v1/workflows/{WF_ID}", "PUT", body)
    live = api(f"/api/v1/workflows/{WF_ID}/activate", "POST", {})
    print("active:", live.get("active"), "nodes:", len(live["nodes"]))

    out = json.dumps(
        {"name": live["name"], "nodes": live["nodes"], "connections": live["connections"], "settings": live.get("settings")},
        indent=2,
        ensure_ascii=False,
    )
    out = re.sub(r"apify_api_[A-Za-z0-9]+", "", out)
    REPO_JSON.write_text(out)


if __name__ == "__main__":
    main()
