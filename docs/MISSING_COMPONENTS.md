# MISSING_COMPONENTS.md

Relative to the cloud-first Shorts factory brief (research→…→learn).  
No implementation in this pass.

## BLOCKERS for the closed product loop

1. **YouTube OAuth `token.json`** — upload/analytics cannot run  
2. **Human approval before publish** — missing; `--upload` publishes immediately when token exists  
3. **Always-on cloud runtime** — no worker/service/deploy config for “Mac off / Cursor closed”  
4. **Object storage** — production still on local `content/` filesystem  

## Core-loop gaps

| Stage | Missing |
| --- | --- |
| Research | Structured opportunity objects (WHY NOW, competition, expected cost, confidence) |
| Decide | Data-driven idea scoring from analytics evidence |
| Script | Timed storyboard with per-scene prompts/transitions/SFX |
| Voice | Provider-independent cloud TTS with timestamps + cost; ElevenLabs via gateway later |
| Visuals | Hybrid scene router (AI video/image/stock/motion) |
| Media gateway | Kie.ai primary + Higgsfield secondary behind `MediaProvider` |
| Model router | Per-scene quality/cost/speed selection |
| Assembly | Cloud Remotion render job (or managed FFmpeg worker) as service |
| Captions | Accurate timestamps (TTS timestamps or cloud ASR) — not length heuristics only |
| Music/SFX | Library + ducking under narration |
| QC | Preview URL + approval record |
| Publish | Schedule + channel selection UX; private-first workflow enforced |
| Analytics | 1h/6h/24h/3d/7d/30d snapshots with retention metrics |
| Learn | Structured lessons with evidence thresholds |
| Experiments | Controlled A/B entities |
| Cost engine | Live provider pricing → cost/short → cost/1k views |
| Jobs | Stage/scene checkpoints, retries, resume |
| Multi-channel | Config isolation beyond one active channel |

## Specifically absent (verified by repo search)

- Any `kie` / `higgsfield` client code  
- `MediaProvider` / `generateImage` / `generateVideo` abstractions  
- Env vars `KIE_API_KEY`, `HF_API_KEY_ID`, `HF_API_KEY_SECRET`  
- S3/GCS/R2 SDKs  
- Deployment manifests (Fly/Render/Railway/ECS/etc.)  

## Present but incomplete

- Remotion template  
- LLM router unused  
- Director/memory tables without real YouTube data  
- Scheduler defined but not deployed  
- Alembic dependency without migrations  
