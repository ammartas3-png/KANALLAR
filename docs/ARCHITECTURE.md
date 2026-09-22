# ARCHITECTURE.md

## Shape

```
n8n Cloud  →  Kanallar Worker (FastAPI)  →  Postgres + Object storage
   │                 │
   │                 ├── MediaProvider (Kie → Higgsfield → local)
   │                 ├── FFmpeg render (Remotion optional)
   │                 └── YouTube Data/Analytics API (OAuth JSON secrets)
   └── Telegram approvals (topic + video)
```

## Principles
1. **n8n** = schedules, approvals, retries, notifications, workflow_runs.
2. **Worker** = research/script/media/render/QC/upload business logic.
3. **Postgres** = source of truth for content status (not n8n history).
4. **Two gates:** topic (before media), video (before publish).
5. **Cost:** no expensive media before topic approval; `DRY_RUN` default.

## Approval
Telegram primary. Tokens issued by worker; only hashes stored. Decisions via `/api/approvals/*/decide`.

## Publish rule
`videos.status` in publishable set **and** consumed `video_approvals` with PUBLISH/APPROVE **and** not `DRY_RUN` for real upload. `AUTO_PUBLISH` stays false.

## Channels
Config in DB + YAML (`tarih-kisa`, `bilim-dakikasi`, `channel_01`). Scale by rows, not hardcoded workflows.
