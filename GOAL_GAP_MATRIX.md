# GOAL_GAP_MATRIX.md

Maps `PROJECT_GOAL.md` → current repo (audit 2026-09-17).  
No new tools proposed here.

| Core-loop stage | Principle touchpoints | Current status | Gap |
| --- | --- | --- | --- |
| YouTube Data (inbound) | 5, 10 | Analytics helpers exist; **no token**, almost no real rows | Complete OAuth; collect snapshots |
| Research | 1, 4 | Catalog + Wikipedia + most-read + yt-dlp titles + Commons refs | Thin competitor patterns; no scored trend model |
| Idea Scoring | 6, 7, 10 | Novelty/heuristic scores; memory read is light | Data-driven scoring from analytics experiments |
| Script | 4, 7, 13 | Template script from catalog facts | Optional LLM later only if quality needs it |
| Voice | 3, 4, 7 | edge → gTTS → espeak working | Music/SFX not present; paid TTS unused (good) |
| Visuals | 3, 4, 13 | Local Pillow cards; Commons attribution only | No real B-roll burn-in yet |
| Edit / 9:16 | 4, 6 | FFmpeg compose works | Remotion unwired duplicate path |
| Subtitles | 4, 13 | ASS estimated word timings | Not ASR-accurate |
| Music/SFX | 3, 13 | None | Add only with free/local licensed assets if QC demands |
| Quality Control | 8, 12, 13 | Strong ffprobe checks | No human approval gate before upload |
| Publishing | 9, 12 | Upload/schedule/playlist code ready | **Blocked on `token.json`**; no explicit approve step |
| YouTube Analytics | 5 | Data API + Analytics API code | Not live without OAuth + published IDs |
| Learning / Memory | 10 | Tables + Director scaffolding | Needs real performance data |
| Next Content Decision | 2, 10 | Used-topic skip + weak hook memory | Must close loop with scored experiments |
| Resume failed jobs | 8 | Jobs mostly restart full pipeline | No stage checkpoint/resume |
| Multi-channel ready | 9 | `channel_id` in DB; one active channel | Scale only after one channel loop works |
| Duplicate tools | 1, 11 | Legacy `kanallar/` + Remotion + unused LLM/Alembic | Cleanup before expansion |

## Fit vs principles (honest)

| Principle | Grade | Note |
| --- | --- | --- |
| 1 Minimum tools | C | Dual stack + unused Remotion/LLM/Alembic |
| 2 Max automation | B- | Produce automated; publish/analytics not closed |
| 3 Low cost | A- | $0 local path works |
| 4 Local/open-source | A- | FFmpeg/Pillow/gTTS first |
| 5 Strong analytics | D | Code yes, data no |
| 6 Modular pipeline | B | Agents separated; legacy muddies replaceability |
| 7 Independently replaceable | B- | Interfaces exist; two implementations in places |
| 8 Resume failed jobs | D | Not implemented |
| 9 Multi-channel ready | C+ | Schema ready; ops single-channel |
| 10 Experiments/lessons | C | Schema + weak Director |
| 11 Avoid duplicates | D | Main debt |
| 12 Human approval before publish | D | `--upload` is immediate if credentials exist |
| 13 Quality over blind automation | B | Original cards/scripts; captions/music weak |

## Execution order (unchanged from audit)

1. Close publish + analytics with existing YouTube libs (**no new service**)  
2. Add human approval flag/default (`upload` requires explicit confirm)  
3. Delete/quarantine duplicate `kanallar/` runtime  
4. Checkpoint/resume for failed stages  
5. Strengthen learning from real analytics  
6. Only then channel 2  

Do not add frameworks/repos/models unless a stage above fails quality or cost tests with current tools.
