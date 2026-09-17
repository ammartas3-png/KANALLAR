# PROJECT_GOAL.md

Canonical product brief for KANALLAR.  
All architecture and cleanup decisions must serve this document.

## Goal

Build a highly automated, low-cost, data-driven YouTube Shorts content factory.

The system should:

1. **RESEARCH** — find trends and successful competitor patterns  
2. **DECIDE** — select topics, hooks and formats using data  
3. **CREATE** — script → voice → visuals → edit → subtitles → music/SFX → final 9:16 Short  
4. **PUBLISH** — automatically upload/schedule to the correct YouTube channel  
5. **ANALYZE** — collect YouTube performance data for every published video  
6. **LEARN** — identify which topics, hooks, formats, durations and publishing strategies perform best  
7. **IMPROVE** — use those findings when generating future videos  

## Architecture principles

1. Minimum number of tools  
2. Maximum automation  
3. Low operating cost  
4. Prefer local/open-source when quality is sufficient  
5. Strong YouTube analytics  
6. Modular pipeline  
7. Every stage must be independently replaceable  
8. Failed jobs must resume instead of restarting  
9. Multi-channel ready  
10. Store historical experiments and lessons  
11. Avoid duplicate tools and unnecessary GitHub repositories  
12. Human approval must be possible before publishing  
13. Never sacrifice content quality just to achieve full automation  

## Scale path

1. Build **ONE** excellent fully working channel pipeline first  
2. Then: 1 channel → 2 channels → 5+ channels  

## Core loop (the product)

```
YouTube Data
  → Research
  → Idea Scoring
  → Script
  → Voice + Visuals
  → Video Production
  → Quality Control
  → Publishing
  → YouTube Analytics
  → Learning / Memory
  → Next Content Decision
```

This feedback loop is the core product.

## Hard constraint

Do **not** add a new framework, repository, AI model or service unless it provides a clear advantage over tools already installed.

See also:

- `CURRENT_ARCHITECTURE.md` — what exists today  
- `MISSING_COMPONENTS.md` — gaps vs this goal  
- `DUPLICATE_OR_UNNECESSARY_TOOLS.md` — KEEP / REMOVE / OPTIONAL  
- `NEXT_STEPS.md` — phased execution order  
