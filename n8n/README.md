# n8n — how this factory runs

Kanallar’ın **birincil işletim sistemi n8n**. Repo’yu her açtığında buradan başla.

## Primary workflow (tek canvas)

| Repo file | Live name |
|-----------|-----------|
| `workflows/primary/youtube-full-pipeline.json` | **PRIMARY: YouTube Full (sade)** |

```
Form / Schedule
  → Gemini + Apify research
  → Sheets queue + scene prompts
  → Telegram (konu)
  → SEO preflight
  → Prototipal video + poll
  → Telegram (video)
  → DRY_RUN? → YouTube Upload
```

Full explanation: [`docs/N8N_HOW_IT_WORKS.md`](../docs/N8N_HOW_IT_WORKS.md).

## Backups (optional)

- `workflows/primary/youtube-otomasyon.json` — sadece araştırma
- `workflows/primary/youtube-paylasim.json` — sadece üretim/yayın
- `workflows/kanallar-shorts-factory.json` — Hybrid / worker upgrade

## n8n Variables

```
DRY_RUN=true
AUTO_PUBLISH=false
```

## Credentials

Google Gemini · Google Sheets · Telegram · YouTube · Apify · Prototipal.

## Absolute rules

1. Workflow’ları credential + dry-run doğrulanmadan **aktif etme**.
2. Secret’leri JSON’a yazma (Apify token → credential).
3. YouTube upload sadece Gate2 + `DRY_RUN=false` iken.
4. Davranış değişince **önce** `n8n/workflows/` güncelle — GitHub her zaman n8n’in nasıl çalıştığını göstersin.
