# PROJECT_STATE.md

**Milestone:** 1 — Foundation (in progress → landing on `main` via PR)  
**Updated:** 2026-09-22

## What works
- Consolidated codebase from prior draft PRs (`cloud-first` + approval + MediaProvider + Docker)
- Explicit state machine (`database/states.py`)
- Expanded schema: approvals, scenes, media_assets, workflow_runs, content_patterns, render_jobs
- Secure approval tokens (`automation/approvals.py`) + HTTP API for Telegram/n8n
- Publish guards: `AUTO_PUBLISH`, `DRY_RUN`, approval row, idempotent `youtube_video_id`
- n8n workflow stubs: `00`, `03`, `07`, `11` under `n8n/workflows/`
- Media default `MEDIA_QUALITY=auto` (Kie → Higgsfield → local)
- Renderer default FFmpeg (cost/perf); Remotion optional

## Current milestone
Milestone 1 foundation complete enough to merge; next is M2 research + topic Telegram loop end-to-end.

## Active issues
- `main` historically empty — this PR consolidates everything
- Live n8n `Youtube Kanlları` workflow is empty — import new JSON
- Worker not yet deployed (no public `KANALLAR_BASE_URL`)
- Kie/HF keys may be unset → local cards fallback
- Legacy `kanallar/` package still present (compat); prefer `automation/`

## Next task
Milestone 2: research shortlist → Telegram topic approval → persist `TOPIC_APPROVED` before any paid media.
