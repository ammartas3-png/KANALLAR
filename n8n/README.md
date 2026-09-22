# n8n — Kanallar orchestration

n8n is the **orchestrator**. The Kanallar worker is the **production brain** (media, render, YouTube OAuth).

## Import

1. Deploy worker; set `KANALLAR_BASE_URL` in n8n Variables (no trailing `/`).
2. Import JSON from `n8n/workflows/` (and optional legacy `n8n/kanallar-cloud-orchestration.json`).
3. Attach **Telegram** credentials in the n8n UI (never commit bot tokens).
4. Activate `00-control-plane` + error handler after health is green.

## Workflow map (M1+)

| File | Purpose |
|------|---------|
| `00-control-plane.json` | Cron → health → workflow_run → produce |
| `03-topic-approval-telegram.json` | Issue topic token + Telegram text |
| `07-video-approval-telegram.json` | Issue video token + preview links |
| `11-error-handler.json` | Sanitize errors for Telegram |

Planned: `01-research`, `02-topic-selection`, `04-script-and-scenes`, `05-media-generation`, `06-render`, `08-youtube-publish`, `09-analytics`, `10-learning`.

## Env / credentials

| Name | Where |
|------|--------|
| `KANALLAR_BASE_URL` | n8n Variable |
| Telegram bot | n8n Credential |
| `N8N_URL` / `N8N_API_KEY` | Cursor Cloud secrets (agent access) |
| `YOUTUBE_*_JSON` | Worker host secrets only |

## Absolute rules

- Do **not** use n8n YouTube Upload node.
- Do **not** put API keys inside workflow JSON.
- Publish only after worker approval APIs succeed (`DRY_RUN` / `AUTO_PUBLISH` respected).
