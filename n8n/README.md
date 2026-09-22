# n8n — Kanallar Hybrid orchestration

## Live workflow

**Name:** `Kanallar Hybrid Shorts (Gate1→Media→Gate2)`  
**Nodes:** 32 · **Active:** false until worker is up

### Money-first order

1. Schedule  
2. Config (`KANALLAR_BASE_URL`)  
3. Health  
4. **`POST /api/research`** — shortlist, **no Kie/render**  
5. Telegram **Topic Gate #1** (APPROVE / REJECT / NEW IDEAS)  
6. On APPROVE → worker produce (hybrid media)  
7. Wait render  
8. Telegram **Video Gate #2** (PUBLISH / REVISE / REJECT)  
9. Worker decide (+ upload only if not DRY_RUN)

## Variables

```
KANALLAR_BASE_URL=https://<worker>
```

## Repo files

| File | Role |
|------|------|
| `kanallar-shorts-factory.json` | Full hybrid canvas (synced to live) |
| `01-research.json` | Subworkflow: research API |
| `02-topic-selection.json` | Shortlist trim |
| `03-topic-approval-telegram.json` | Topic token stub |
| `07-video-approval-telegram.json` | Video token stub |
| `00-control-plane.json` / `11-error-handler.json` | Control / errors |

## Absolute rules

- Never start produce before topic APPROVE in this hybrid plan  
- Never use n8n YouTube node  
- Keep inactive until `/health` is green  
