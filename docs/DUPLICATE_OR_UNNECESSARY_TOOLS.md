# DUPLICATE_OR_UNNECESSARY_TOOLS.md

## Duplicates (same job twice)

| Keep | Remove later (after test migration) | Why |
| --- | --- | --- |
| `automation/pipeline.py` | `kanallar/pipeline.py` | Two factories |
| `apps/studio/` | `kanallar/web/` | Two UIs |
| `voice/provider.py` | `kanallar/tts.py` | Two TTS stacks |
| `video/slides.py` | `kanallar/slides.py` + `thumbnail.py` | Two visual gens |
| `video/ffmpeg.py` + compose | `kanallar/video.py` | Two assemblers |
| `youtube/api.py` | `kanallar/youtube_upload.py` | Two upload helpers |
| SQLAlchemy videos/jobs | `kanallar/store.py` | Two persistence models |
| `channels/channel_01/` | `channels/bilim-dakikasi.yaml`, `tarih-kisa.yaml`, `kanallar/catalog/` | Dual channel/catalog formats |
| Factory tests | Legacy tests importing `kanallar.*` | Dual test surface |

**Do not delete in this audit turn** — wait for approval, then migrate tests first.

## Unnecessary / premature for V1 cloud brief

| Item | Why |
| --- | --- |
| Local Ollama / AirLLM / local Whisper / local SD | Explicitly out of scope |
| browser-use for YouTube upload | Official API preferred |
| OpenMontage vendor | Overlaps entire app |
| Agent frameworks (LangGraph, agency-*, gstack…) | Custom agents already modular |
| n8n as core engine | Optional orchestration only |
| Remotion + FFmpeg both “primary” without choice | Pick one cloud assembly path for V1 |
| Alembic without migrations | Dead dependency |
| Unused LLM/Pexels/paid-TTS env surface | Noise until wired |

## Complexity that is unnecessary today

1. Claiming Remotion support while produce always FFmpeg  
2. Maintaining legacy `kanallar/` after CLI redirect  
3. Settings for Anthropic/Gemini/Ollama with no callers  
4. Analytics/Director pretending closed-loop without YouTube token  
