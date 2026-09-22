# PROJECT_STATE.md

**Milestone:** Single PRIMARY full pipeline (otomasyon+paylasim merged)  
**Updated:** 2026-09-22

## What works
- **One workflow to use:** `PRIMARY: YouTube Full Pipeline (otomasyon+paylasim)` (71 nodes) on live n8n
- Section A = research/prompt; Section B = Prototipal + YouTube with DRY_RUN guard
- Bridge: `onaylandi` → paylasim path
- Split PRIMARY workflows kept as backup only

## Current milestone
Operate the merged pipeline; link credentials; dry-run smoke test.

## Active issues
- Credentials still need linking in n8n UI
- Apify/Prototipal/YouTube OAuth on n8n side
- Postgres dual-gate upgrades still next

## Next task
User opens **Full Pipeline** only, connects credentials, sets `DRY_RUN=true`, runs form once.
