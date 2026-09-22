# n8n — Kanallar orchestration

n8n is the **orchestrator**. The Kanallar worker is the **production brain**.

## Live instance

- URL: `https://ammartd20.app.n8n.cloud`
- Main plan workflow: **Kanallar Shorts Factory (n8n plan)** (was empty `Youtube Kanlları`)
- Status: **inactive** until `KANALLAR_BASE_URL` + worker are ready

### Work plan (nodes 1→18)

1. Daily Schedule 08:00 UTC  
2. Factory Config (`KANALLAR_BASE_URL`)  
3. Worker Health  
4. Worker OK?  
5. Start `workflow_run` / Telegram if down  
6. Dispatch `/api/produce`  
7. Wait ~4 min (render)  
8. List pending videos  
9–10. Pick pending  
11. Issue video approval token  
12–14. Telegram Approval #2 (PUBLISH / REVISE / REJECT links)  
15. Wait human webhook  
16–17. Decide on worker (+ optional upload)  
18. Telegram result  

Topic Approval #1 arrives in Milestone 2 (`03-topic-approval-telegram.json`).

## Import / sync

Files under `n8n/workflows/`:

| File | Purpose |
|------|---------|
| `kanallar-shorts-factory.json` | **Full live plan** (source of truth for main canvas) |
| `00-control-plane.json` | Slim cron skeleton |
| `03-topic-approval-telegram.json` | Topic gate stub → expand M2 |
| `07-video-approval-telegram.json` | Video gate stub |
| `11-error-handler.json` | Error notify stub |

## n8n Variables (required)

```
KANALLAR_BASE_URL=https://<your-worker>   # no trailing slash
```

Telegram credential already on instance: **Telegram account** (chat `1240141730`).

## Absolute rules

- Do **not** use n8n YouTube Upload node (OAuth stays on worker).
- Do **not** put API keys in workflow JSON.
- Keep workflow **inactive** until worker `/health` is green.
- `DRY_RUN=true` / `AUTO_PUBLISH=false` on worker until you explicitly go live.
