# IMPLEMENTATION_ROADMAP.md

Wait for approval before coding. Phases match the brief.

## Phase 1 — ONE excellent Short pipeline (cloud artifacts)

Goal: one high-quality Short end-to-end **without** requiring public publish.

1. Freeze features; migrate/remove legacy duplicate stack (tests first).  
2. Add job stage machine + resume.  
3. Storyboard JSON with timed scenes.  
4. Introduce `MediaProvider` (even if first adapter is “local cards / gTTS”).  
5. Move outputs to object storage + Postgres.  
6. QC + preview URL.  

Exit: previewable Short in cloud storage with full metadata.

## Phase 2 — Automated YouTube publishing

1. Finish OAuth token.  
2. Human approval gate.  
3. Private upload + schedule + playlist.  
4. Store YouTube video IDs on `uploads`.  

Exit: approved Short appears private on the correct channel.

## Phase 3 — Analytics collection

1. Data API stats + Analytics API reports.  
2. Snapshots: 1h / 6h / 24h / 3d / 7d / 30d.  
3. Dashboard metrics from real data.  

## Phase 4 — Learning system

1. Structured lessons with evidence thresholds.  
2. Idea scoring reads lessons.  
3. Experiments A/B.  
4. Cost/1k views.  

## Phase 5 — Channel 2

Same engine, new channel config + credentials + memory.

## Phase 6 — 5+ channels

Scheduler isolation, quotas, shared worker pool, per-channel budgets.

## Hybrid media insertion point (after Phase 1 scaffolding)

1. Implement `KieProvider` as primary gateway (verify models via https://kie.ai/market).  
2. Implement `HiggsfieldProvider` as secondary.  
3. Scene router chooses asset type + provider + model.  
4. Assembler (FFmpeg and/or Remotion cloud) stitches results.  

## n8n placement (if used)

**In n8n:** schedules, approval notifications, “run analytics poll”, dead-letter alerts.  
**In app:** research scoring, storyboard, provider routing, QC rules, learning logic, YouTube API calls.

## Hard stop

No installs/deletes/rewrites until this roadmap is approved.
