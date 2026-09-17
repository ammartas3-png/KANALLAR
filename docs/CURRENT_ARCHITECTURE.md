# CURRENT_ARCHITECTURE.md

Audit date: 2026-09-17  
Branch: `cursor/automated-youtube-studio-71b0`  
Constraint honored: inspection only — no installs, deletes, or rewrites.

## Executive verdict

The repo already contains a **working single-channel Shorts factory** that can research → script → TTS → FFmpeg 9:16 → QA on cloud/Cursor agents.

It does **not** yet implement the cloud-first hybrid AI-video product described in the new brief:

- No Kie.ai / Higgsfield integration  
- No provider-independent `MediaProvider`  
- No object storage (production files are local `content/`)  
- No resumable scene-level job system  
- No human-approval gate before upload  
- YouTube OAuth token missing → publish/analytics loop incomplete  
- Dual codebase (`automation/*` vs legacy `kanallar/*`)

## What runs today (canonical path)

```
channels/channel_01/{config,catalog}.yaml
        ↓
agents: research → idea → script → asset → voice → QA → upload → analytics → director
        ↓
voice/provider.py   (edge-tts → gTTS → espeak)
        ↓
video/compose.py    (Pillow cards + FFmpeg + ASS captions)
        ↓
SQLite (default) or PostgreSQL schema
content/videos/<id>/final.mp4
```

Entry: `python3 -m automation produce|studio|analytics|channel`  
Compat: `python3 -m kanallar …` redirects to the same factory for `channel_01`.

## Module map

| Area | Path | State |
| --- | --- | --- |
| Pipeline | `automation/pipeline.py` | Working |
| Agents | `agents/*_agent/` | Working heuristics; no LLM calls |
| Studio | `apps/studio/` | Working FastAPI UI |
| Remotion | `apps/remotion/` | Template only; **not called by produce** |
| Voice | `voice/provider.py` | Working cloud-ish TTS (gTTS works) |
| Video | `video/*` | FFmpeg assembly working |
| YouTube | `youtube/*` | Code ready; needs `token.json` |
| DB | `database/*` | Models + schema; Alembic unused |
| Research | `research/*` | Wiki/trends/Commons/yt-dlp meta |
| Legacy | `kanallar/*` | Duplicate stack still present |
| Docs (prior) | repo root `*.md` | Earlier audit; superseded by `docs/` |

## Data / config

| Item | Reality |
| --- | --- |
| `.env` | Present locally; gitignored; SQLite default |
| `.env.example` | Documents many unused keys |
| `client_secret.json` | Present on agent disk; gitignored; **not in git** |
| `token.json` | Absent |
| Active channel | `channel_01` (Bilim Dakikası) |
| Tests | 20 passed |
| CI | GitHub Actions pytest |

## Cloud-first gap (vs brief §2)

Current production artifacts live under gitignored **local filesystem** (`content/`, `data/`). There is no S3/GCS/R2 layer, no always-on worker service definition, and scheduler must be started manually. Cursor/GitHub are used; true unattended cloud runtime is **not deployed**.
