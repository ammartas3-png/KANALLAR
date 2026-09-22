# PRIMARY STACK — Cursor şablonları

**Karar (2026-09-22):** Ana tema = Cursor’ın verdiği `youtube-otomasyon` + `youtube-paylasim`.  
Kanallar Hybrid parçaları **sonra** performans için eklenir.

## Canlı n8n (inactive)

| Workflow | ID | Nodes |
|----------|-----|------:|
| PRIMARY: youtube-otomasyon (Cursor) | `ceTtnEGNt5srPnQm` | 47 |
| PRIMARY: youtube-paylasim (Cursor+safety) | `WGeALMqtdsab3kkw` | 21 |
| Kanallar Hybrid (önceki omurga, referans) | `pOUFteeJt9G8chOL` | 32 |

## Akış (ana tema)

```
[otomasyon]
Form → Gemini keywords → Apify YouTube scrape → Gemini konu/başlık/sahne
→ Google Sheets → Telegram onay

[paylasim]
Schedule → Sheets tarih/içerik → Prototipal VIDEO olustur → poll
→ Telegram onay → indir → DRY_RUN guard → YouTube Upload (n8n node)
```

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
