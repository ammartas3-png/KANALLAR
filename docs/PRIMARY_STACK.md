# PRIMARY STACK — Cursor şablonları

**Karar (2026-09-22):** Ana tema = Cursor’ın verdiği `youtube-otomasyon` + `youtube-paylasim`.  
Kanallar Hybrid parçaları **sonra** performans için eklenir.

## Canlı n8n — hangisini açacaksın

**Tek kullan:** `PRIMARY: YouTube Full (sade)` (`Xu72EtzVvMUHnBvO`)

Nasıl çalışır (repo’da her zaman güncel): [`N8N_HOW_IT_WORKS.md`](N8N_HOW_IT_WORKS.md).

İçerik = Cursor iki şablon + ince ekler: `DRY_RUN?`, A→B köprü, **SEO preflight**.

Ayrı `otomasyon` / `paylasim` / Hybrid = yedek.

## Bizden eklenecek / eklendi performans noktaları

| Özellik | Durum | Neden |
|---------|--------|--------|
| `DRY_RUN` / upload IF | **Eklendi** | Yanlışlıkla canlı publish engeli |
| SEO preflight (AgentTube pattern) | **Eklendi** | Başlık/açıklama bozukken Prototipal parası yakma |
| `AUTO_PUBLISH=false` env | Dokümante | Mutlak güvenlik |
| Çift kapı (konu + video) | Cursor’da var; token’lı harden **sonra** | Güvenlik |
| Analytics 24h/7d learn | **Sonra** (AgentTube pattern) | Kazanç döngüsü |
| Postgres state machine | **Sonra** (Sheets yanında mirror) | Retry / analytics |
| Catalog+trend ucuz research | **Sonra** Apify maliyeti yüksekse fallback | Birim ekonomisi |
| FFmpeg hybrid / Kie wow | **Sonra** Prototipal pahalı/kalitesizse | Maliyet |
| Worker YouTube OAuth | **Opsiyonel** n8n YT node sorun çıkarırsa | Tek token |

## Gerekli n8n credentials / env

- Google Gemini (PaLM) API  
- Google Sheets OAuth  
- Telegram  
- YouTube OAuth (**n8n node** — ikinci Google consent gerekebilir)  
- Apify token (URL içinde / credential)  
- Prototipal gateway erişimi  
- Variables: `DRY_RUN=true`, `AUTO_PUBLISH=false`

## Repo dosyaları

- `n8n/workflows/primary/youtube-otomasyon.json`
- `n8n/workflows/primary/youtube-paylasim.json` (safety node’lu)
