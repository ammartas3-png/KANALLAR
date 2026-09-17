# NEXT_STEPS.md

Ordered plan. **No new feature work in this audit turn.**  
Principle: finish the loop you already have before adding tools.

---

## Phase 0 — Freeze (now)

1. Stop adding renderers, agents, or channels.
2. Treat `automation/pipeline.py` + `apps/studio` as the only product surface.
3. Do not install n8n, Remotion Whisper, browser-use, or paid video APIs.

---

## Phase 1 — Make upload/analytics real (highest ROI)

1. Complete Google OAuth once (browser consent) → produce `token.json`.
2. Run:
   ```bash
   python3 -m automation produce --topic <unused> --upload
   ```
3. Confirm video appears **private** on YouTube.
4. Run `python3 -m automation analytics` and verify `analytics` rows.
5. Only then judge DirectorAgent usefulness.

**Exit criteria:** one private Short on YouTube + one analytics snapshot in DB.

---

## Phase 2 — Architecture cleanup (no new capabilities)

Do this before multi-channel:

1. Migrate legacy tests off `kanallar.*` onto factory modules.
2. Delete or quarantine:
   - `kanallar/web`, `kanallar/pipeline`, duplicate TTS/slides/video/youtube/store
   - leftover `channels/*.yaml` at root (keep `channel_01/`)
3. Either:
   - **A)** delete Remotion from runtime claims (`RENDERER`, npm as optional docs), or  
   - **B)** wire `RENDERER=remotion` properly with one CI smoke  
   Pick one. Prefer **A** for minimum tools.
4. Remove Alembic from requirements **or** add real migrations.
5. Fix schema evolution story (migration or explicit `reset_db` script) so `time_window`-class renames cannot brick SQLite.

**Exit criteria:** one CLI, one UI, one compose path, tests green without legacy imports.

---

## Phase 3 — Strengthen the self-improving loop (still one channel)

1. Snapshot schedule: 1h / 6h / 24h / 3d / 7d for uploaded videos.
2. Persist experiment results (`winning` / `losing`) from view thresholds.
3. Feed memory into research/idea selection with measurable rules (not vibes).
4. Dashboard: best/worst video, cost/1k views with real denominators.
5. Run scheduler under supervision (cloud cron or `automation.scheduler`) for daily produce + analytics.

**Exit criteria:** next topic choice changes because of measured performance.

---

## Phase 4 — Cost & quality levers (only if Phase 3 needs them)

Evaluate in this order (cheapest first):

1. Better free/offline TTS (e.g. Piper) if gTTS quality blocks retention  
2. Optional cheap LLM for hooks/titles only (`LLMProvider` already stubbed)  
3. Commons/Pexels stills as actual B-roll (license/attribution pipeline)  
4. Remotion word-highlight captions if ASS readability fails  

Do **not** start with Veo/Kling/ElevenLabs.

---

## Phase 5 — Multi-channel

Only after Phases 1–3:

1. `channels/channel_02` config + catalog  
2. Per-channel upload token or clear brand-channel mapping  
3. Scheduler jobs per channel with frequency caps  
4. Shared core, isolated memory/experiments  

---

## Explicit non-goals (reject unless goal changes)

- n8n as primary orchestrator  
- OpenMontage vendoring  
- LangGraph / agent swarms  
- Redis / Kubernetes  
- Browser automation for YouTube Studio upload  
- Reuploading others’ footage via yt-dlp  

---

## Immediate operator checklist (this week)

| # | Action | Owner |
| --- | --- | --- |
| 1 | Merge or keep PR; CI already green | You |
| 2 | OAuth → `token.json` | You (browser) |
| 3 | First `--upload` private Short | You / cloud agent |
| 4 | Approve Phase 2 cleanup PR scope | You |
| 5 | No new features until Phase 1 done | Both |

---

## Success metric for “done enough”

A single channel that, without Mac installs:

1. Produces a Short in cloud  
2. Uploads private via official API  
3. Pulls analytics  
4. Stores learning memory  
5. Schedules the next produce  

…using **one** pipeline and **no** duplicate stacks.
