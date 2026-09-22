# PROJECT_STATE.md

**Milestone:** Primary stack pivot — Cursor otomasyon + paylasim  
**Updated:** 2026-09-22

## What works
- Cursor workflows imported to live n8n as **PRIMARY** (inactive)
- `youtube-paylasim` hardened with **DRY_RUN upload guard**
- Prior Kanallar Hybrid kept as reference workflow on instance
- Docs: PRIMARY_STACK, GITHUB_RESEARCH, DECISIONS updated

## Current milestone
Operate on Cursor theme first; layer Kanallar performance pieces next.

## Active issues
- Credentials must be re-linked in n8n UI (Gemini, Sheets, Apify, Prototipal, YouTube)
- Apify token may be embedded in node URLs — rotate / move to credentials
- n8n YouTube node = separate OAuth from Mac worker token
- Sheets remains source of truth until Postgres mirror lands

## Next task
1. User links credentials + sets `DRY_RUN=true`  
2. Smoke-test otomasyon (form → Sheets) without publish  
3. Add Postgres approval/audit mirror + topic gate tokens from Kanallar  
