# Ideas from darkzOGx/youtube-automation-agent (AgentTube)

Source: https://github.com/darkzOGx/youtube-automation-agent (~3.6k★, MIT, Node/SQLite dashboard — **not** n8n).

We **do not vendor** their app. We borrow **patterns** that fit our Cursor n8n + optional Python worker stack.

## Worth adopting (priority)

| Idea | Why it earns | How we add it (n8n-first) | Status |
|------|--------------|---------------------------|--------|
| Approval-first publish | Prevents bad uploads | Telegram Gate1 (otomasyon) + Gate2 (paylasim) + `DRY_RUN` | **Done** |
| SEO / packaging preflight | Better CTR before paying Prototipal | Code node: title length, description present, format | **Done** (primary) |
| Resume / checkpoint | Don’t re-pay for finished stages | Sheets `durum` column as queue state (`planlandı`→`onaylandı`→…) | **Partial** — document + keep Sheets |
| Post-publish analytics loop | Learn what retains | Worker / later n8n: 24h + 7d snapshot → Telegram summary | Roadmap |
| Scene-aware retention | Fix hooks that drop viewers | Only when we own scene timeline (FFmpeg/hybrid path) | Later |
| Controlled title/thumb A/B | Prove packaging | YouTube metadata swap after publish — high risk; manual only | Later |
| Audience comments → ideas | Free research | Sync comments → Gemini themes → Sheet ideas (read-only drafts) | Later |
| Production readiness probe | Fail before spend | n8n cron: health + Sheets + Telegram “ready?” | Next |
| Daily cost caps | Protect wallet | `MAX_DAILY_VIDEOS` / env already in worker; mirror in n8n If | Next |

## Skip / don’t copy

| Idea | Reason |
|------|--------|
| Full Node dashboard + SQLite | We already chose **n8n + Sheets** as primary OS |
| DarkzSEO Python adapter | Extra product; optional later if needed |
| Auto comment replies | ToS / brand risk; drafts only if ever |
| Cloning their agents into `/agents` | License OK (MIT) but stack mismatch; patterns only |

## Rule

Anything we take must stay **visible in `n8n/workflows/`** and explained in `docs/N8N_HOW_IT_WORKS.md`.
