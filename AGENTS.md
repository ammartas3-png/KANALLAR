# AGENTS.md

Compact map for Cursor / Claude / ChatGPT working on **KANALLAR**.

## Goal
Cloud-first AI YouTube Shorts factory: **n8n orchestrates**, Python worker renders/uploads. Two human gates (Telegram): topic before media, video before publish.

## Read order
1. `AGENTS.md` (this file)
2. `docs/PROJECT_STATE.md`
3. Only files for the current task

## Layout
| Path | Role |
|------|------|
| `n8n/workflows/` | Importable orchestration JSON (no secrets) |
| `automation/` | Pipeline, worker, approvals, jobs |
| `apps/studio/` | FastAPI health + Studio + n8n HTTP API |
| `media/` | Kie.ai / Higgsfield / local MediaProvider |
| `video/` | FFmpeg (default) + optional Remotion |
| `youtube/` | Official Data + Analytics API (OAuth on worker) |
| `database/` | Postgres models + state machine |
| `channels/` | Per-channel YAML |
| `docs/` | Architecture / decisions / roadmap |

## Non-negotiables
- `AUTO_PUBLISH=false`, `DRY_RUN=true` until operator flips
- No publish without `video_approvals` + approved status
- No n8n YouTube OAuth node (second credential)
- No secrets in git / workflow JSON
- Do not clone OpenMontage (AGPL) into the repo
- Paid Kie/HF calls only when keys set and not dry-run media path

## Dev memory ≠ content memory
- Dev: `docs/PROJECT_STATE.md`, `DECISIONS.md`
- Content: DB `memory`, `content_patterns`, analytics
