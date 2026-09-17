# MISSING_COMPONENTS.md

Audit of gaps versus the stated goal:  
**minimum tools + maximum automation + low cost + strong analytics + self-improving multi-channel Shorts factory.**

Status legend: **BLOCKER** / **MVP_GAP** / **LATER**

---

## 1. YouTube authorization loop — BLOCKER (for upload/analytics)

| Missing | Evidence |
| --- | --- |
| `token.json` | `credentials_status() → token: False` |
| First OAuth browser consent | Upload path requires interactive Desktop OAuth |
| Verified private upload | Never completed end-to-end in this environment |
| Analytics snapshots from real videos | `AnalyticsAgent` no-ops without uploads/token |

Until token exists, factory is **produce + QA only**.

---

## 2. Analytics / learning loop — MVP_GAP

| Missing | Impact |
| --- | --- |
| Real views/CTR/retention ingestion | Director only sees empty/zero experiments |
| Snapshot windows 1h/6h/24h/3d/7d as first-class jobs | Scheduler has 1h + 24h only; no 6h/3d/7d |
| Cost / 1k views on dashboard | Field present as `0` placeholder |
| Subscriber metric wiring | Dashboard hardcodes `subscribers: 0` |
| Feedback into research/script prompts | IdeaAgent reads memory lightly; no closed-loop scoring |

Self-improving factory is **scaffolded**, not proven.

---

## 3. Multi-channel — LATER (by design for MVP) but incomplete scaffolding

| Missing | Notes |
| --- | --- |
| Stable multi-channel config only under `channels/<id>/` | Leftover `bilim-dakikasi.yaml`, `tarih-kisa.yaml` |
| Per-channel credentials | Single global `client_secret.json` / `token.json` |
| Per-channel schedules beyond one cron | Scheduler loads `ACTIVE_CHANNEL` only |
| Isolation of used topics / memory per brand at scale | Tables support `channel_id`, ops do not |

---

## 4. Video engine completeness — MVP_GAP

| Missing | Notes |
| --- | --- |
| `RENDERER=remotion` path in pipeline | Setting exists; produce always FFmpeg |
| Word-accurate captions from ASR | ASS timings are length-weighted estimates |
| B-roll / Commons image burn-in | Commons refs attributed in description only |
| Background music / SFX | Explicitly none (good for cost; gap vs checklist) |
| Remotion render CI | No headless Chrome render in CI |

---

## 5. LLM / agent intelligence — MVP_GAP

| Missing | Notes |
| --- | --- |
| Agents calling `LLMProvider` | Router exists; research/idea/script are catalog heuristics |
| Cheap/normal/premium routing in produce | Env vars unused in pipeline |
| Competitor analysis depth | yt-dlp titles only; no structured scoring |
| Google Trends | Not integrated (Wikipedia most-read used instead) |

Low cost is achieved by **not using LLMs**, which also caps quality variance.

---

## 6. Database operations — MVP_GAP

| Missing | Notes |
| --- | --- |
| Alembic migrations | Package installed; no config/versions |
| Auto-migrate on schema rename | SQLite drift broke Director until DB delete |
| Postgres as default in cloud `.env` | Currently SQLite for reliability |

---

## 7. Scheduler / ops — MVP_GAP

| Missing | Notes |
| --- | --- |
| Process supervision for scheduler | Manual start only |
| Failure alerts | No Slack/email |
| Idempotent daily produce lock | Can double-produce if overlapping |
| n8n | Intentionally absent |

---

## 8. Logging / observability — MVP_GAP

| Missing | Notes |
| --- | --- |
| File logs in `logs/` | Directory empty |
| Structured log levels | Decorator DB rows only |
| Per-video cost breakdown UI | Aggregate fields exist |

---

## 9. QA gaps vs original checklist — MVP_GAP

Implemented: resolution, aspect, duration, audio, captions size, blackdetect, silence, duplicate narration, size.

Still weak / missing:

- True “voice intelligibility” (only silence heuristic)
- Script↔video semantic alignment
- Copyright risk beyond “no stock music / original cards”
- Retention prediction

---

## 10. Security / secrets hygiene — MVP_GAP

| Item | Status |
| --- | --- |
| `client_secret.json` gitignored | OK |
| Secret uploaded into agent workspace | Present on disk; must not be committed |
| `.env` committed? | Local `.env` exists; should stay gitignored (is) |
| OAuth consent app in Testing | Operator must keep test user list |

---

## 11. Empty / unfinished modules

| Module | State |
| --- | --- |
| `research/browser.py` | Stub; raises “ikinci aşama” |
| `video/remotion.py` | Helper only; unused by pipeline |
| `config/llm.py` | Unused by agents |
| `database/migrations/` | Empty |
| Paid TTS branches | Message only, no API clients |
| Codebase Memory MCP | Disabled in `.cursor/mcp.json` |

---

## Summary: what is missing for the stated main goal

1. **YouTube OAuth token + first private upload** (unlocks analytics)  
2. **Collapse / quarantine legacy `kanallar/` stack** (architecture clarity)  
3. **Wire or delete Remotion/LLM/Alembic surface area** (stop pretend options)  
4. **Real analytics → Director → next idea loop with non-zero data**  
5. **Only then** multi-channel
