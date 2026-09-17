# CLOUD_SERVICES_REQUIRED.md

Accounts/services needed for the recommended architecture.  
**None of the AI media gateways are integrated yet.**

## Already partially in place

| Service | Status | Action |
| --- | --- | --- |
| GitHub | Working | Keep |
| Cursor Cloud Agents | Dev/runtime today | Dev only long-term |
| Google Cloud project `Kanallar` | YouTube APIs enabled | Keep |
| YouTube OAuth Desktop client | `client_secret.json` exists | Complete consent → `token.json` |
| PostgreSQL | Optional local/VM | Move to managed Postgres |

## Required for closed loop (minimum)

| Service | Free vs paid | Purpose |
| --- | --- | --- |
| Google YouTube Data API + Analytics | Free quota / Google account | Upload + metrics |
| Managed Postgres (Neon/Supabase/RDS/etc.) | Free tier possible → paid | Online DB |
| Object storage (Cloudflare R2 / S3 / GCS) | Low paid | Durable media |
| Always-on worker host (Fly/Render/Railway/Cloud Run/VM) | Paid | Produce when Mac/Cursor off |
| Secrets store (platform env secrets) | Usually included | Keys/tokens |

## Recommended for hybrid media quality (after approval)

| Service | Role | Free vs paid |
| --- | --- | --- |
| **Kie.ai** | Primary media gateway (image/video/audio/LLM market) | Paid credits; see https://kie.ai/pricing |
| **Higgsfield** | Secondary/premium/fallback generative media | Paid; see Higgsfield Cloud |
| Optional OpenAI-compatible LLM | Scripts/hooks if heuristics insufficient | Paid |
| Optional ElevenLabs (direct or via Kie) | Premium consistent voice | Paid |

## Optional orchestration

| Service | Role |
| --- | --- |
| n8n Cloud | Cron, Slack/Telegram approval, analytics poll triggers |

## Explicitly NOT required for V1

- Local GPU box  
- Ollama / local Whisper / local SD  
- Browser-use for YouTube Studio  
- OpenMontage install  

## API keys you will need (names only)

- `YOUTUBE` OAuth client + refresh token (files/env)  
- `DATABASE_URL` (managed Postgres)  
- `STORAGE_*` (bucket credentials)  
- `KIE_API_KEY` (when integrating Kie)  
- `HF_API_KEY_ID` + `HF_API_KEY_SECRET` (when integrating Higgsfield)  
- Optional `OPENAI_API_KEY` / other LLM  
- Optional music library keys if stock audio used  

Never commit these. Never paste values into chat/docs.
