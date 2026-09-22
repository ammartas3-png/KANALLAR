# PROJECT_STATE.md

**Milestone:** 2 — Hybrid research + topic gate (in progress)  
**Updated:** 2026-09-22

## What works
- Milestone 1 foundation (state machine, approvals, publish guards)
- **Hybrid strategy applied:** topic research → Telegram Gate #1 → produce → Gate #2
- `POST /api/research` builds scored shortlist **without media spend**
- Topic APPROVE can auto-start produce (`start_produce=true`)
- Media plan: `MEDIA_QUALITY=hybrid`, Kie only wow roles, `MAX_KIE_SCENES_PER_VIDEO=1`
- Live n8n: **Kanallar Hybrid Shorts (Gate1→Media→Gate2)** — 32 nodes, inactive until worker URL

## Current milestone
M2 hybrid path coded + live n8n updated. Needs worker deploy + `KANALLAR_BASE_URL` to run E2E.

## Active issues
- Worker not deployed publicly
- Catalog-only research (YouTube competitor signals light); OK for MVP cost
- Kie async fetch into assembler still “planned” for wow scenes (cards until keyed+wired)
- Modular 01/02 JSON exist; main live canvas is the full hybrid plan

## Next task
Milestone 3–4: wire wow-scene Kie job poll into render; harden `/render` job API; QC before Gate #2.
