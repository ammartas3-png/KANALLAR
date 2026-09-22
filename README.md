# Kanallar

Cloud-first YouTube Shorts factory.

## Primary stack (Cursor templates)

n8n workflows:

1. **youtube-otomasyon** — Form → Gemini → Apify → Sheets → Telegram  
2. **youtube-paylasim** — Schedule → Prototipal video → Telegram → YouTube (`DRY_RUN` guard)

Docs: [`docs/PRIMARY_STACK.md`](docs/PRIMARY_STACK.md) · [`docs/GITHUB_RESEARCH.md`](docs/GITHUB_RESEARCH.md) · [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md)

## Upgrade kit (our hybrid — add when needed)

- Cheap research / FFmpeg path / Postgres state / dual approval tokens  
- Live reference workflow: Kanallar Hybrid Shorts  

## Safety

Defaults: `DRY_RUN=true`, `AUTO_PUBLISH=false`. Never commit secrets.
