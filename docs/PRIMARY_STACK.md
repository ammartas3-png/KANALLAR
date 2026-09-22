# PRIMARY STACK — Cursor şablonları

**Karar (2026-09-22):** Ana tema = Cursor’ın verdiği `youtube-otomasyon` + `youtube-paylasim`.  
Kanallar Hybrid parçaları **sonra** performans için eklenir.

## Canlı n8n — hangisini açacaksın

**Tek kullan:** `PRIMARY: YouTube Full (sade)` (`Xu72EtzVvMUHnBvO`)

Nasıl çalışır: [`N8N_HOW_IT_WORKS.md`](N8N_HOW_IT_WORKS.md).

Canvas: üst = araştırma/prompt, alt = video/YouTube (orijinal Cursor kutuları, arada boşluk).
Ekler: SEO preflight + `DRY_RUN?` + onaylandi→tarih köprüsü.

Canlıda silinen (bizim kopyalar): ayrı otomasyon, ayrı paylasim, Hybrid Shorts.  
Repo yedekleri: `n8n/workflows/primary/*` + `n8n/archive/` (eski stub’lar).


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
- Telegram (chat id `8715342169` — @istanbul1453_1923)  
- YouTube OAuth (**n8n node** — ikinci Google consent gerekebilir)  
- Apify token (URL içinde / credential)  
- Prototipal gateway erişimi  
- Variables: `DRY_RUN=true`, `AUTO_PUBLISH=false`

## Repo dosyaları

- `n8n/workflows/primary/youtube-otomasyon.json`
- `n8n/workflows/primary/youtube-paylasim.json` (safety node’lu)
