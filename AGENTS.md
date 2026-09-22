# AGENTS.md

Compact map for Cursor / Claude / ChatGPT working on **KANALLAR**.

## Goal
Cloud-first AI YouTube Shorts factory. **Primary OS = n8n** (Cursor full pipeline). Python worker is an upgrade kit. Two human gates (Telegram): topic before media, video before publish.

## Read order
1. `docs/AKIS.md` — **step-by-step production flow** (required for ChatGPT/Claude/Cursor)
2. `docs/N8N_HOW_IT_WORKS.md` — short n8n map
3. `n8n/README.md` — import / credentials
4. `AGENTS.md` (this file)
5. `docs/PROJECT_STATE.md`
6. Only files for the current task

## Layout
| Path | Role |
|------|------|
| `n8n/workflows/primary/` | **Source of truth** for daily production JSON |
| `n8n/workflows/` | Hybrid + modular stubs |
| `docs/N8N_HOW_IT_WORKS.md` | Always keep accurate with live n8n behavior |
| `automation/` | Pipeline, worker, approvals, jobs (upgrade) |
| `apps/studio/` | FastAPI health + Studio + Hybrid HTTP API |
| `media/` | Kie.ai / Higgsfield / local MediaProvider |
| `video/` | FFmpeg (default) + optional Remotion |
| `youtube/` | Official Data + Analytics API (worker path) |
| `database/` | Postgres models + state machine (upgrade) |
| `channels/` | Per-channel YAML |
| `docs/` | Architecture / decisions / roadmap |

## Non-negotiables
- GitHub must always show how n8n works (`docs/N8N_HOW_IT_WORKS.md` + `n8n/workflows/primary/`)
- `AUTO_PUBLISH=false`, `DRY_RUN=true` until operator flips
- Primary path may use **n8n YouTube Upload node**; worker YouTube OAuth is optional fallback
- No secrets in git / workflow JSON
- Do not clone OpenMontage (AGPL) or AgentTube wholesale into the repo
- Paid Kie/HF calls only when keys set and not dry-run media path

## Dev memory ≠ content memory
- Dev: `docs/PROJECT_STATE.md`, `DECISIONS.md`
- Content: DB `memory`, `content_patterns`, analytics
