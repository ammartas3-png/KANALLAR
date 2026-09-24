# INSTALLED_TOOLS_AUDIT.md

Classification: **KEEP** / **REMOVE** / **OPTIONAL** / **NOT CONFIGURED** / **BROKEN**

## Python (`requirements.txt`)

| Package | Role | Class | Notes |
| --- | --- | --- | --- |
| fastapi, uvicorn, jinja2, python-multipart | Studio | KEEP | Needed for preview UI |
| pydantic, pydantic-settings | Config | KEEP | |
| PyYAML | Channel/catalog | KEEP | |
| httpx | HTTP research/LLM stub | KEEP | |
| pillow | Card visuals | KEEP | Current visual path |
| gTTS | TTS | KEEP | Works in this environment |
| edge-tts | TTS preferred | KEEP | Often blocked; keep as first try |
| SQLAlchemy | ORM | KEEP | |
| psycopg[binary] | Postgres | KEEP | Cloud DB path |
| pytest | Tests | KEEP | |
| google-api-python-client, google-auth, google-auth-oauthlib | YouTube | KEEP | Official API |
| yt-dlp | Competitor metadata | OPTIONAL | Metadata only; never reupload |
| APScheduler | Cron jobs | OPTIONAL | Not required until unattended cloud worker |
| alembic | Migrations | REMOVE or finish | **NOT CONFIGURED** (no alembic.ini/versions) |

## System tools (environment)

| Tool | Class | Notes |
| --- | --- | --- |
| ffmpeg / ffprobe | KEEP | Assembly + QA |
| espeak-ng | OPTIONAL | Last TTS fallback |
| Node 20 + npm | OPTIONAL | Only for Remotion path |
| PostgreSQL | KEEP (target) | Schema ready; `.env` often SQLite |

## Node (`apps/remotion`)

| Package | Class | Notes |
| --- | --- | --- |
| remotion, @remotion/cli, react, react-dom | OPTIONAL | Template installed; produce ignores it |
| node_modules | OPTIONAL / heavy | Not needed for current FFmpeg MVP |

## Internal modules

| Module | Class | Notes |
| --- | --- | --- |
| `automation/*` | KEEP | Canonical |
| `apps/studio/*` | KEEP | Canonical UI |
| `agents/*` | KEEP | Modular stages |
| `video/compose.py` + ffmpeg/captions/slides | KEEP | Live assembler |
| `voice/provider.py` | KEEP | Replaceable TTS interface (partial) |
| `youtube/*` | KEEP | Official API surface |
| `database/*` | KEEP | Needs migration discipline |
| `kanallar/*` runtime duplicates | REMOVE later | Do not delete in this audit turn |
| `config/llm.py` | NOT CONFIGURED | Unused by agents |
| `video/remotion.py` | NOT CONFIGURED | Unwired |
| `research/browser.py` | NOT CONFIGURED | Stub raises |
| Paid TTS branches | NOT CONFIGURED | Env only |
| Kie.ai client | NOT CONFIGURED | **Absent** |
| Higgsfield client | NOT CONFIGURED | **Absent** |
| Object storage SDK | NOT CONFIGURED | Absent |
| MediaProvider interface | NOT CONFIGURED | Absent |
| Human approval gate | NOT CONFIGURED | `--upload` is immediate |
| Scene resume/checkpoints | NOT CONFIGURED / effectively BROKEN vs goal | Full restart only |

## Environment variables

| Variable | Class | Used by runtime? |
| --- | --- | --- |
| DATABASE_URL | KEEP | Yes |
| ACTIVE_CHANNEL | KEEP | Yes |
| KANALLAR_HOST/PORT | KEEP | Studio |
| YOUTUBE_CLIENT_SECRETS / YOUTUBE_TOKEN | KEEP | Yes |
| RENDERER | NOT CONFIGURED | Settings only; ignored by pipeline |
| OPENAI_* / LLM_* / ANTHROPIC / GEMINI / OLLAMA | NOT CONFIGURED | LLMProvider unused |
| VOICE_PROVIDER | NOT CONFIGURED | Channel YAML used instead |
| ELEVENLABS_API_KEY / GOOGLE_TTS_API_KEY | NOT CONFIGURED | No clients |
| PEXELS_API_KEY / YOUTUBE_API_KEY | NOT CONFIGURED | Unused |
| KIE_API_KEY / HF_* | NOT CONFIGURED | Not in project |

## Secrets hygiene

| Check | Result |
| --- | --- |
| Secrets tracked in git? | No |
| `.gitignore` covers `.env`, `client_secret.json`, `token.json`, media? | Yes |
| `client_secret.json` on agent disk | Present (local only) |
| `token.json` | Absent |
| Secret values printed in docs? | No |
