# CURRENT_ARCHITECTURE.md

Audit date: 2026-09-17  
Repo: `ammartas3-png/KANALLAR`  
Branch audited: `cursor/automated-youtube-studio-71b0`  
Scope: full tree (excluding `node_modules`, `.git`, generated `content/`, `.pytest_cache`)

## Verdict

There is **one intended production core** and **one legacy parallel stack**.

| Layer | Canonical path | Status |
| --- | --- | --- |
| Entry CLI | `python3 -m automation` | Working |
| Compatibility CLI | `python3 -m kanallar` → redirects to factory | Working (thin wrapper) |
| Pipeline | `automation/pipeline.py` | Working end-to-end (local Shorts) |
| Studio | `apps/studio` | Working |
| Legacy studio/pipeline | `kanallar/web`, `kanallar/pipeline.py` | Still present; **not** the intended runtime |
| Tests | `pytest` | **20 passed** (CI green) |

**Goal fit today:** minimum-cost local Shorts factory for **one** channel (`channel_01`). Multi-channel, strong YouTube analytics loop, and paid LLM/TTS are **declared but not fully operational**.

---

## System diagram (as implemented)

```
channels/channel_01/config.yaml + catalog.yaml
            │
            ▼
 ResearchAgent → IdeaAgent → ScriptAgent → AssetAgent
            │
            ▼
 VoiceAgent (edge-tts → gTTS → espeak)
            │
            ▼
 video/compose.py (Pillow slides + FFmpeg + ASS captions)
            │
            ▼
 QAAgent → (optional) UploadAgent → AnalyticsAgent → DirectorAgent
            │
            ▼
 SQLite (default) / PostgreSQL (schema ready)
 + content/videos/<id>/final.mp4
 + agent_runs / memory / experiments tables
```

Remotion (`apps/remotion`) exists as a **template**, but the live pipeline always calls `video.compose.compose_short` (FFmpeg). `RENDERER=remotion` is **not wired**.

---

## Folder map

| Path | Role | Notes |
| --- | --- | --- |
| `agents/` | Research, idea, script, asset, voice, QA, upload, analytics, director | Heuristic/local; no LLM calls in agents |
| `analytics/` | `cost_per_video`, dashboard queries | Works against DB; YouTube metrics need OAuth token |
| `apps/studio/` | FastAPI dashboard | Canonical UI |
| `apps/remotion/` | Shorts React template | Installed deps; **not used by produce** |
| `automation/` | CLI, pipeline, scheduler, agent logging | Core |
| `channels/` | `channel_01/` MVP + leftover YAML | Dual config formats |
| `config/` | settings, paths, LLM router | LLM router unused by agents |
| `content/` | Generated videos (gitignored) | Runtime artifact store |
| `database/` | models, schema.sql, session | Alembic listed but unused |
| `database/migrations/` | Empty | Placeholder |
| `kanallar/` | Legacy package | Duplicate pipeline/UI/TTS/store |
| `memory/` | Channel memory helpers + local index script output | Director writes win/lose hooks |
| `research/` | Wikipedia, trends, Commons, yt-dlp meta, browser stub | Browser not implemented |
| `scripts/` | DB bootstrap, codebase index | Useful |
| `templates/shorts/` | Schema JSON only | Docs for Remotion/FFmpeg flow |
| `tests/` | Unit/integration | Mix of legacy + factory tests |
| `video/` | Captions, slides, FFmpeg, Remotion helper | Live compose path |
| `voice/` | TTS provider interface | Live |
| `youtube/` | Data API upload + Analytics helper + playlists | Upload needs `token.json` |
| `logs/` | Empty dir | No file logger yet |

---

## Runtime entry points

| Command | Behavior |
| --- | --- |
| `python3 -m automation produce [--topic] [--upload]` | Full factory |
| `python3 -m automation studio` | Dashboard |
| `python3 -m automation channel` | Print active channel |
| `python3 -m automation analytics` | Pull analytics if token present |
| `python3 -m automation.scheduler` / `automation/scheduler.py` | APScheduler jobs defined |
| `python3 -m kanallar produce …` | Alias → same factory (`channel_01` only) |

---

## Video generation pipeline (live)

1. Topic pick from catalog (skip used topics)
2. Research: Wikipedia summary + most-read trends + optional yt-dlp metadata
3. Idea + script JSON (`hook`, scenes, CTA)
4. Assets: local cards; Commons stills as **attribution refs only** (not burned in as B-roll)
5. Voice: `voice/provider.py`
6. Compose: slides → zoompan clips → concat → loudnorm voice → optional ASS burn → `final.mp4`
7. QA: 1080×1920, 9:16, duration, audio, captions, blackdetect, silence, duplicate narration
8. Upload only if `--upload` and credentials exist
9. Director learns from experiments/analytics (weak until real views exist)

Proven in cloud: e.g. tardigrade Short ~38s, QA pass, cost `$0`.

---

## Database / storage

| Item | Status |
| --- | --- |
| SQLAlchemy models | Present: channels, ideas, scripts, videos, uploads, analytics, experiments, memory, agent_runs, used_topics |
| `database/schema.sql` | Present; Postgres reserved-word fix (`time_window`) |
| Default `.env` | `sqlite:///./data/kanallar.db` |
| Postgres | Bootstrap script exists; can run locally in cloud VM |
| Alembic | In `requirements.txt`, **no `alembic.ini` / versions** → NOT operational |
| Media | `content/videos/<id>/` on disk |
| Secrets | `client_secret.json` gitignored; `token.json` **missing** |

Schema drift risk: SQLite created before `time_window` rename can break Director until DB reset (`create_all` does not migrate).

---

## API integrations

| Integration | Code | Configured | Live |
| --- | --- | --- | --- |
| YouTube Data API upload | `youtube/api.py` | `client_secret.json` yes | No — needs OAuth browser → `token.json` |
| Thumbnail set | yes | same | blocked by token |
| Playlist add | `youtube/playlists.py` | `playlist_id` empty | not used |
| Schedule `publishAt` | supported in upload | not used by CLI | dormant |
| YouTube Analytics v2 | `youtube/analytics.py` | scopes declared | not configured (no token) |
| Wikipedia / Commons | httpx | none needed | working |
| yt-dlp metadata | research | package installed | optional network |
| OpenAI / Anthropic / Gemini / Ollama | `config/llm.py` | env empty | unused by agents |
| ElevenLabs / Google TTS paid | settings only | empty | stub fallback messages |
| Pexels | settings only | empty | unused |
| browser-use | stub only | n/a | raises |

---

## Logging

- Agent decorator `automation/logging.py` writes `agent_runs` rows (input/output JSON, duration, token, cost, error).
- No rotating file logs under `logs/`.
- Studio/produce stdout is the operator log.

---

## Scheduler

`automation/scheduler.py`:

- daily produce 08:00 UTC
- analytics hourly
- analytics daily 07:30 UTC

Not started by default; not wired into studio or CI. Single-channel only.

---

## Tests / CI

- Local/CI: **20 passed**
- CI workflow: install + pytest with SQLite
- Coverage gap: no full `produce()` integration test in CI (heavy ffmpeg/TTS); Remotion render untested; YouTube upload untested (needs secrets)

---

## Dual-stack debt (critical architecture fact)

Legacy `kanallar/` still contains:

- own SQLite job store
- own pipeline / TTS / slides / video / YouTube upload
- own FastAPI templates

New stack duplicates many of those concerns under `video/`, `voice/`, `youtube/`, `apps/studio/`.

Compatibility CLI points to the new factory, but **legacy modules remain importable and several tests still target them**.

This is the main structural risk for “minimum tools” and long-term maintainability.
