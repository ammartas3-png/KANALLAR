# FINAL_AUDIT_REPORT.md

Senior architecture audit for **Automated YouTube Shorts Factory**.  
Date: 2026-09-17. **STOP after this report — awaiting approval.**

Supporting docs in `docs/`:

- CURRENT_ARCHITECTURE.md  
- INSTALLED_TOOLS_AUDIT.md  
- GITHUB_REPOSITORIES_AUDIT.md  
- MISSING_COMPONENTS.md  
- DUPLICATE_OR_UNNECESSARY_TOOLS.md  
- RECOMMENDED_CLOUD_ARCHITECTURE.md  
- CLOUD_SERVICES_REQUIRED.md  
- IMPLEMENTATION_ROADMAP.md  
- KIE_AND_HIGGSFIELD_CHECK.md  

---

## 1. What currently works?

- Single-channel produce pipeline (`automation/pipeline.py`)
- Research heuristics (catalog + Wikipedia + trends + optional yt-dlp titles)
- Script/scenes generation from catalog
- Cloud-capable TTS waterfall (gTTS proven here)
- Pillow visual cards + FFmpeg 1080×1920 Short + ASS captions
- QA checks (resolution, aspect, duration, audio, black/silence, duplicate)
- Studio dashboard (FastAPI)
- SQLAlchemy schema for channels/ideas/scripts/videos/uploads/analytics/experiments/memory/agent_runs
- YouTube upload/playlist/schedule/analytics **code**
- Agent run logging + basic cost aggregation hooks
- Pytest: **20 passed**; CI green
- Google project APIs enabled by operator; `client_secret.json` present (gitignored)

## 2. What is partially implemented?

- Remotion Shorts template (not wired into produce)
- LLM router (`config/llm.py`) unused by agents
- Director/learning memory without real YouTube performance fuel
- Scheduler (defined, not deployed as always-on service)
- Multi-channel readiness (DB `channel_id`, one active channel)
- Voice “provider independence” (local waterfall only)
- Analytics snapshots (code path; no live token/data)
- Compatibility CLI over legacy package

## 3. What is broken?

- Publish/analytics loop without `token.json`
- Schema drift risk on SQLite when columns change (no real migrations)
- Goal principle “resume failed jobs” — **not implemented** (full restart)
- Goal principle “human approval before publish” — **not implemented**
- Claimed `RENDERER=remotion` — **ineffective**
- Legacy `kanallar/` still importable; tests still depend on it → architectural contradiction

## 4. What is missing?

- Kie.ai + Higgsfield + MediaProvider + model router  
- Hybrid scene asset decisions (AI video/image/stock/motion)  
- Storyboard with timed prompts/SFX/transitions  
- Music/SFX ducking layer  
- Accurate caption timestamps (cloud ASR/TTS alignment)  
- Object storage + managed online DB as production default  
- Always-on cloud worker/deploy  
- Structured experiments + evidence-based lessons  
- Live cost engine from provider pricing  
- n8n (optional) orchestration decisions implemented  

## 5. What should be removed? (later, after approval)

- Duplicate `kanallar/` runtime modules (after test migration)
- Root leftover channel YAMLs / duplicated catalogs
- Alembic dependency **or** unfinished state (pick one)
- Dead env knobs that imply capabilities that don’t exist
- Dual-renderer ambiguity until one cloud assembly path is chosen

## 6. What GitHub repositories should remain?

**Remain / keep using:** Google API client libs, current app code, optional Remotion package, optional yt-dlp.  

**Do not install now:** OpenMontage, browser-use, OpenViking, agent frameworks, AirLLM/Ollama stacks, FreeLLMApi, G0DM0D3, etc.  

**Consider later:** official `higgsfield-client` only behind MediaProvider; codebase-memory MCP optional.

## 7. What cloud services/accounts do I need?

See `CLOUD_SERVICES_REQUIRED.md`. Minimum: Google/YouTube OAuth, managed Postgres, object storage, always-on worker, secrets. Recommended next: Kie.ai, Higgsfield, optional n8n Cloud, optional LLM.

## 8. What API keys will I need?

Names only: YouTube OAuth secrets/token, `DATABASE_URL`, storage credentials, `KIE_API_KEY`, Higgsfield key id/secret, optional LLM key, optional music/stock keys.

## 9. Which services are free vs paid?

| Free / freemium | Paid |
| --- | --- |
| YouTube API quota (limited) | Kie.ai credits |
| Wikipedia/Commons | Higgsfield usage |
| gTTS/edge-tts (fragile/ToS risk) | Managed Postgres beyond free tier |
| FFmpeg compute on your worker | Object storage + egress |
| | Always-on host |
| | Premium TTS/LLM if added |

## 10. Approximate cost per video?

**Today’s path (cards + gTTS + FFmpeg):** ~**$0.00–$0.05** compute on a small worker (often ~$0 media).  

**Hybrid AI-video path (future):** **do not hard-code**; depends on scene mix and https://kie.ai/pricing / Higgsfield pricing. Expect order-of-magnitude jump when multiple AI video scenes are used. Cost engine must read live pricing, not guesses.

## 11. What should run in our backend?

Core product logic: research scoring, storyboard, provider routing, job state machine, QC rules, approval records, YouTube API calls, analytics ingestion, learning/experiments, cost accounting, channel configs.

## 12. What should run in n8n, if anything?

Optional: cron triggers, Slack/Telegram “approve?” buttons, alerting, simple poll schedules. **Not** storyboard/provider/QC business rules.

## 13. What should Kie.ai handle?

Primary generative gateway: image/video/audio/LLM market models via one async API. Verify current catalog on https://kie.ai/market before wiring model IDs.

## 14. What should Higgsfield handle?

Secondary/premium/fallback generative media when Kie lacks quality/reliability for a scene type. Official platform API + SDKs.

## 15. What should Remotion/FFmpeg handle?

**Assembly only:** 9:16 sequencing, captions, overlays, audio mix, final encode. Not AI clip generation. Current production uses FFmpeg; Remotion is a polish candidate.

## 16. Database/storage architecture?

- **DB:** managed Postgres (channels, ideas, jobs/stages/scenes, assets, providers, costs, uploads, analytics snapshots, experiments, lessons)  
- **Storage:** object store with clear prefixes `channels/{id}/videos/{video_id}/{scripts,voice,scenes,renders,final,thumbs}`  
- **Secrets:** platform secret manager / env — never git  

## 17. Exact path ZERO → FIRST finished Short (with current repo)

1. Use existing factory (already done once in cloud).  
2. `python3 -m automation produce --topic <id>`  
3. Preview `content/videos/<id>/final.mp4` / studio.  
4. (Quality bar for “excellent” hybrid AI Short is **not** met by cards alone — needs MediaProvider work after approval.)

## 18. Exact path first Short → full automation

OAuth token → approval gate → private upload → analytics snapshots → learning writes lessons → scheduler triggers next produce using lessons → worker runs with Cursor/Mac off.

## 19. Exact path one channel → 5+ channels

Stabilize loop on `channel_01` → add `channel_02` config+creds+memory → shared worker pool + per-channel budgets/schedules → scale configs only.

## 20. Unnecessarily complex today

- Dual stacks (`kanallar` + new factory)  
- Remotion installed but unused while docs imply choice  
- Unused LLM/multi-provider env surface  
- Learning/analytics UI without YouTube token  
- Alembic listed without migrations  

---

## Kie + Higgsfield summary

| Question | Answer |
| --- | --- |
| Kie integrated? | **No** |
| Higgsfield integrated? | **No** |
| Models configured? | **None** |
| Working media APIs? | Local/open TTS+FFmpeg only |
| Missing env? | `KIE_API_KEY`, `HF_API_KEY_ID`, `HF_API_KEY_SECRET` |
| Duplicate AI gateways? | No (zero gateways) |
| Abstraction ready? | **No** — need `MediaProvider` first |

---

## STOP

No repositories installed.  
No components deleted.  
No major rewrite started.  
No first hybrid video generation started.

**Waiting for your approval** before implementation.
