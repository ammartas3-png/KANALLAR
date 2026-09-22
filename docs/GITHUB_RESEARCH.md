# GitHub research — high-signal Shorts automation

Survey date: 2026-09-22. Used to decide what to **borrow as patterns**, not to vendor whole repos.

## High-star / notable projects

| Stars | Repo | License | Class | Takeaway for us |
|------:|------|---------|-------|-----------------|
| ~14k | FujiwaraChoki/MoneyPrinter | MIT | DO NOT USE whole | Viral toy; ToS/quality risk; pattern only |
| ~8k | RayVentura/ShortGPT | MIT | REFERENCE | Pipeline stages (script→asset→edit) |
| ~5k | Anil-matcha/AI-Youtube-Shorts-Generator | MIT | OPTIONAL later | Long→Short clip; not our faceless script path |
| ~3.7k | mutonby/openshorts | MIT | REFERENCE | Self-host clip factory; heavy |
| ~2.3k | rushindrasinha/youtube-shorts-pipeline | MIT | REFERENCE | Orchestration ideas |
| ~2.1k | Hao0321/video-autopilot-kit | MIT | REFERENCE | Kit structure |
| ~690 | eat-pray-ai/yutu | Apache-2.0 | OPTIONAL | YouTube CLI/API helper |
| ~505 | SamurAIGPT/AI-Faceless-Video-Generator | MIT | REFERENCE | Faceless stack map |
| ~227 | SaarD00/AI-Youtube-Shorts-Generator | MIT | **USEFUL PATTERN** | Gemini + Edge-TTS + FFmpeg (matches our hybrid cost path) |
| ~182 | (same family) | MIT | OPTIONAL | — |
| ~1632 | lucaswalter/n8n-ai-automations | ? | REFERENCE | n8n AI examples |
| ~108 | mismai-li/n8n-youtube-to-shorts-workflow | MIT | REFERENCE | n8n + external render poll loops (like Prototipal) |
| ~74 | Hritikraj8804/Autotube | MIT | REFERENCE | n8n + Docker + local AI |
| ~71 | aruntemme/n8n-faceless-youtube | MIT | REFERENCE | Sheets → assemble → YouTube (similar to Cursor) |
| ~60k | remotion-dev/remotion | Source+company | OPTIONAL | Polish renderer |
| ~60k | calesthio/OpenMontage | **AGPL-3.0** | **DO NOT USE** | License + duplicate |
| ~3.6k | darkzOGx/youtube-automation-agent | MIT | **PATTERNS** | Approval-first, SEO preflight, analytics learn, resume — see `IDEAS_FROM_AGENTTUBE.md` |

## Alignment with chosen primary (Cursor)

Cursor stack already mirrors common n8n templates:
- Sheets as queue (like aruntemme)
- External render API + poll (like mismai-li / Prototipal)
- LLM topic/scene (Gemini vs OpenAI)
- n8n YouTube upload node

**Best upgrades from GitHub + Kanallar (priority order):**
1. Hard publish guards (`DRY_RUN`) — done on paylasim  
2. Explicit dual human gates with durable records (Postgres)  
3. Cheap FFmpeg path when Prototipal cost/quality hurts (SaarD00 pattern)  
4. Analytics learning loop (few repos do this well — keep ours)  
5. Avoid MoneyPrinter-style uncontrolled spam  

## Decision

Primary = Cursor JSON workflows.  
Borrow patterns from SaarD00 / Autotube / n8n-youtube-to-shorts.  
Do not clone OpenMontage or MoneyPrinter into the repo.
