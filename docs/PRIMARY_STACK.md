# PRIMARY STACK — Cursor şablonları

**Karar (2026-09-22):** Ana tema = Cursor’ın verdiği `youtube-otomasyon` + `youtube-paylasim`.  
Kanallar Hybrid parçaları **sonra** performans için eklenir.

## Canlı n8n — hangisini açacaksın

**Tek kullan:** `PRIMARY: YouTube Full (sade)` (`Xu72EtzVvMUHnBvO`)

İçerik = Cursor’ın iki şablonunun toplamı (görünüş sade, node sayısı onlarınki kadar).
Bizden ekstra sadece: `DRY_RUN?` kapısı + A→B köprüsü.

Ayrı `otomasyon` / `paylasim` / Hybrid = yedek.

## Bizden eklenecek / eklendi performans noktaları

| Özellik | Durum | Neden |
|---------|--------|--------|
| `DRY_RUN` / upload IF | **Eklendi** paylaşıma | Yanlışlıkla canlı publish engeli |
| `AUTO_PUBLISH=false` env | Dokümante | Mutlak güvenlik |
| Çift kapı (konu + video) | Kısmen Cursor’da var; token’lı harden **sonra** | Güvenlik |
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
