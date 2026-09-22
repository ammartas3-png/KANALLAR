# Kanallar

Cloud-first **AI YouTube Shorts** factory.

- **n8n Cloud** orchestrates schedules, Telegram approvals, retries.
- **Python worker** runs research → script → Kie/Higgsfield/local media → FFmpeg render → QC → YouTube Data API.
- **Two human gates (Telegram):** topic before media; final video before publish.
- Defaults: `AUTO_PUBLISH=false`, `DRY_RUN=true`.

Read: [`AGENTS.md`](AGENTS.md) → [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) → [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Channels (MVP)

- `channel_01` / Bilim Dakikası
- `tarih-kisa`, `bilim-dakikasi` YAML configs

## Quick start

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
bash scripts/bootstrap_db.sh
pytest -q
python3 -m automation studio --host 0.0.0.0 --port 8080
```

Docker: `docker compose up --build`.

## n8n

Import `n8n/workflows/*.json`. Set `KANALLAR_BASE_URL`. Wire Telegram in n8n UI. See [`n8n/README.md`](n8n/README.md).

## Safety

Never commit `token.json`, `client_secret.json`, `.env`, or n8n bot tokens. No automatic YouTube publish without Approval #2.
