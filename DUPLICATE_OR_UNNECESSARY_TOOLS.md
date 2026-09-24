# DUPLICATE_OR_UNNECESSARY_TOOLS.md

Classification for every meaningful dependency, GitHub-related tool, and internal duplicate.

Legend: **KEEP** / **REMOVE** / **OPTIONAL** / **NOT CONFIGURED**

---

## A. Internal duplicates (highest priority)

| Item | Duplicate of | Classification | Recommendation |
| --- | --- | --- | --- |
| `kanallar/pipeline.py` | `automation/pipeline.py` | **REMOVE** (after test migration) | Dead parallel factory |
| `kanallar/web/` | `apps/studio/` | **REMOVE** | Old dashboard |
| `kanallar/tts.py` | `voice/provider.py` | **REMOVE** | Same TTS waterfall |
| `kanallar/slides.py` + `thumbnail.py` | `video/slides.py` | **REMOVE** | Same Pillow cards |
| `kanallar/video.py` | `video/ffmpeg.py` + compose | **REMOVE** | Same FFmpeg path |
| `kanallar/youtube_upload.py` | `youtube/api.py` | **REMOVE** | Older upload helper |
| `kanallar/store.py` (SQLite jobs) | SQLAlchemy `videos`/`agent_runs` | **REMOVE** | Dual persistence |
| `kanallar/config.py` + root YAMLs | `channels/loader.py` + `channel_01/` | **REMOVE** leftover configs | Keep only `channels/<id>/` |
| `channels/bilim-dakikasi.yaml` | `channels/channel_01/` | **REMOVE** | Alias already in CLI |
| `channels/tarih-kisa.yaml` | future channel_02 | **OPTIONAL** | Do not activate until MVP stable |
| `kanallar/catalog/*.yaml` | `channels/channel_01/catalog.yaml` | **REMOVE** or single-source | Duplicated science catalog |
| Tests targeting legacy (`test_config`, `test_store`, `test_render`, `test_tts`, `test_topics_and_script`) | `test_factory.py` | **REMOVE**/rewrite | Currently preserve 20 green via legacy |

---

## B. Python packages (`requirements.txt`)

| Package | Role | Classification | Notes |
| --- | --- | --- | --- |
| fastapi, uvicorn, jinja2, python-multipart | Studio UI | **KEEP** | Needed for dashboard |
| pydantic, pydantic-settings | Config/models | **KEEP** | |
| PyYAML | Channel/catalog | **KEEP** | |
| httpx | Wiki/Commons/LLM | **KEEP** | |
| pillow | Slides/thumbs | **KEEP** | |
| gTTS | TTS fallback that works in cloud | **KEEP** | Primary working voice today |
| edge-tts | Preferred TTS | **KEEP** | Often 403 in some networks; keep as first try |
| SQLAlchemy | ORM | **KEEP** | |
| psycopg[binary] | Postgres driver | **KEEP** | Even if SQLite default |
| pytest | Tests | **KEEP** | |
| google-api-python-client, google-auth, google-auth-oauthlib | YouTube | **KEEP** | Core upload/analytics |
| yt-dlp | Research metadata only | **OPTIONAL** | Keep if competitor titles useful; else drop to reduce surface |
| APScheduler | Cron-like jobs | **OPTIONAL** | Keep code; not required until daily automation |
| alembic | Migrations | **REMOVE** or finish | Currently **NOT CONFIGURED** — dead weight |
| (system) ffmpeg/ffprobe | Encode/QA | **KEEP** | Not pip; mandatory |
| (system) espeak-ng | Last TTS fallback | **OPTIONAL** | Nice offline safety |

---

## C. Node / Remotion (`apps/remotion`)

| Item | Classification | Notes |
| --- | --- | --- |
| remotion + @remotion/cli + react | **OPTIONAL** | Template present; **not used by produce** |
| Remotion node_modules (~250 pkgs) | **OPTIONAL** / heavy | Do not treat as runtime MVP dependency |
| `video/remotion.py` | **OPTIONAL** | Unwired helper |
| `RENDERER` env | **NOT CONFIGURED** in practice | Always FFmpeg path |

**Architect recommendation:** keep Remotion as a **future polish track**, or delete until FFmpeg path is insufficient. Do not maintain two renderers “half-on”.

Official related repos considered:

| Repo | Classification | Why |
| --- | --- | --- |
| remotion-dev/remotion | **OPTIONAL** | Already vendored as npm deps |
| remotion-dev/template-tiktok + Whisper.cpp | **REMOVE** from MVP plan | Large models; ASR cost/complexity |
| OpenMontage (calesthio) | **OPTIONAL** inspiration only | Do **not** vendor; too many paid/tooling deps |

---

## D. External GitHub / MCP / services

| Tool / repo | Classification | Notes |
| --- | --- | --- |
| yt-dlp/yt-dlp | **OPTIONAL** | Metadata-only; never download for reupload |
| DeusData/codebase-memory-mcp | **OPTIONAL** / **NOT CONFIGURED** | Disabled in `.cursor/mcp.json` |
| `scripts/index_codebase.py` | **KEEP** (cheap local substitute) | |
| browser-use/browser-use | **REMOVE** from MVP | Stub only; upload must stay official API |
| Piper TTS | **OPTIONAL** later | Better offline voice; not installed |
| n8n | **REMOVE** from current architecture | Explicitly deferred; Python scheduler enough |
| LangGraph / Redis / K8s / OpenViking / swarm | **REMOVE** | Violate minimum-tools goal |
| Wikimedia Commons API | **KEEP** | Free attributed refs |
| Wikipedia REST | **KEEP** | Free research |

---

## E. Environment variables

| Variable | Classification | Reality |
| --- | --- | --- |
| `DATABASE_URL` | **KEEP** | Used |
| `ACTIVE_CHANNEL` | **KEEP** | Used |
| `KANALLAR_HOST/PORT` | **KEEP** | Studio bind (CLI flags also) |
| `YOUTUBE_CLIENT_SECRETS` / `YOUTUBE_TOKEN` | **KEEP** | Used |
| `RENDERER` | **NOT CONFIGURED** | Read by settings; **ignored by pipeline** |
| `OPENAI_*` / `LLM_*` | **NOT CONFIGURED** | LLMProvider unused by agents |
| `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` | **NOT CONFIGURED** | Settings only |
| `OLLAMA_BASE_URL` | **NOT CONFIGURED** | Settings only; `available()` treats URL as truth even without server |
| `VOICE_PROVIDER` | **NOT CONFIGURED** | Settings field; voice uses **channel YAML** provider |
| `ELEVENLABS_API_KEY` / `GOOGLE_TTS_API_KEY` | **NOT CONFIGURED** | No client code |
| `PEXELS_API_KEY` | **NOT CONFIGURED** | Unused |
| `YOUTUBE_API_KEY` | **NOT CONFIGURED** | OAuth used instead; key unused |

---

## F. “Unnecessary for minimum tools” shortlist

Delete or freeze first (when rewrite is allowed):

1. Legacy `kanallar/` runtime (keep temporarily only until tests moved)  
2. Alembic until migrations are real  
3. Remotion runtime path **or** finish wiring — not both half-done  
4. Unused LLM/paid TTS/Pexels env surface from `.env.example` (or mark clearly dormant)  
5. Second channel YAML until channel_01 analytics loop works  
6. browser-use stub unless second-phase research is scheduled  

Keep ruthlessly:

- FFmpeg compose + Pillow cards + gTTS/edge waterfall  
- SQLAlchemy + one DB  
- YouTube official API  
- One studio  
- One pipeline  
- Catalog-driven research until LLM proves ROI
