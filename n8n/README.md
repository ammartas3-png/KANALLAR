# Kanallar / n8n

## Primary (Cursor theme) — use these first

Import / live:

- `n8n/workflows/primary/youtube-otomasyon.json` — research + Gemini + Apify + Sheets + Telegram
- `n8n/workflows/primary/youtube-paylasim.json` — Prototipal render + Telegram + YouTube (with `DRY_RUN` guard)

See `docs/PRIMARY_STACK.md`.

### n8n Variables

```
DRY_RUN=true
AUTO_PUBLISH=false
```

## Secondary (Kanallar Hybrid) — performance upgrades

- `n8n/workflows/kanallar-shorts-factory.json` — Gate1→media→Gate2 worker path
- Worker APIs under `/api/research`, `/api/approvals/*`

## Absolute rules

- Keep workflows **inactive** until credentials linked and dry-run verified
- Do not commit API tokens; scrub Apify tokens from URLs into n8n credentials
- Prefer human Telegram approval before YouTube upload (already in paylasim)
