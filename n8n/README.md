# n8n — how this factory runs

Kanallar’ın **birincil işletim sistemi n8n**. Repo’yu her açtığında buradan başla.

## Primary (tek workflow)

| Repo | Live n8n |
|------|----------|
| `workflows/primary/youtube-full-pipeline.json` | **PRIMARY: YouTube Full (sade)** |

Canvas düzeni:
- **Üst blok** — araştırma + prompt + konu onayı (sarı/yeşil kutular)
- **Alt blok** — tarih → SEO → Prototipal → video onayı → YouTube

```
Form / Schedule
  → Gemini + Apify
  → Sheets + scene prompts
  → Telegram (konu)
  → SEO preflight
  → Prototipal + poll
  → Telegram (video)
  → DRY_RUN? → YouTube
```

Detay: [`docs/N8N_HOW_IT_WORKS.md`](../docs/N8N_HOW_IT_WORKS.md)

## Backups (opsiyonel, canlıda yok)

- `workflows/primary/youtube-otomasyon.json`
- `workflows/primary/youtube-paylasim.json`

Eski Hybrid / stub’lar: `n8n/archive/` (kullanma).

## Variables

```
DRY_RUN=true
AUTO_PUBLISH=false
```

## Credentials

Gemini · Sheets · Telegram · YouTube · Apify · Prototipal.

## Rules

1. Credential + dry-run olmadan **aktif etme**.
2. Secret JSON’a yazma.
3. Canlıda sadece **Full (sade)** kalsın; kopya PRIMARY / Hybrid silindi.
4. Davranış değişince önce git’teki `primary/` JSON’u güncelle.
