# DECISIONS.md

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-22 | n8n is orchestrator; Python is worker | Operator requirement; reuse existing factory |
| 2026-09-22 | Telegram for both approval gates | Mobile, already used in n8n account |
| 2026-09-22 | Merge all draft PR work into one `main` line | No parallel abandoned factories |
| 2026-09-22 | Media: Kie.ai primary, Higgsfield secondary | Operator choice; local fallback if keys missing |
| 2026-09-22 | Render default FFmpeg; Remotion optional | Best cost/perf; Remotion license risk for automation |
| 2026-09-22 | Do not vendor OpenMontage | AGPL + duplicates stack |
| 2026-09-22 | Primary path may use n8n YouTube Upload node | Matches Cursor templates; worker OAuth remains optional fallback |
| 2026-09-22 | Primary OS docs always explain n8n (`N8N_HOW_IT_WORKS`) | GitHub must show how production runs |
| 2026-09-22 | Borrow AgentTube patterns only (SEO preflight now) | Do not vendor their Node/SQLite app |
| 2026-09-22 | `AUTO_PUBLISH=false`, `DRY_RUN=true` defaults | Absolute safety |
| 2026-09-22 | **Hybrid money path** | Topic gate before media; local cards default; ≤1 Kie wow scene |
| 2026-09-22 | Research = catalog + Wikipedia most-read signals | Cheap, auditable scores — not “LLM viral” |
| 2026-09-22 | **PRIMARY = Cursor `youtube-otomasyon` + `youtube-paylasim`** | Operator chose their templates as main theme |
| 2026-09-22 | Kanallar Hybrid becomes upgrade kit | Add DRY_RUN (done), dual-gate tokens, cheap FFmpeg fallback, analytics later |
| 2026-09-22 | GitHub: borrow SaarD00/Autotube/n8n-shorts patterns; skip OpenMontage/MoneyPrinter | Stars ≠ production fit; AGPL/spam risk |

| 2026-09-22 | Primary OS = n8n; docs always explain n8n | Repo clarity for operators |
| 2026-09-22 | Borrow AgentTube patterns (SEO now, analytics later); do not vendor Node app | Keep Cursor/n8n stack |
