# ChatGPT review — Cursor değerlendirmesi

Kaynak: [`CHATGPT_WORKFLOW_REVIEW.md`](CHATGPT_WORKFLOW_REVIEW.md) (2026-09-23).  
Claude’dan henüz repo’da review yok.

Genel hüküm: **Review doğru ve yerinde.** Omurgayı koruyor, öncelik sırası mantıklı. Birkaç maddede n8n Cloud gerçekleriyle ince ayar gerekiyor (aşağıda).

## Madde madde

| # | Öneri | Katılıyor muyuz | Durum |
|---|-------|-----------------|-------|
| 2 | Gate 1 = gerçek konu seçimi (3–5 aday, 1/2/3 seç) | **Evet, en değerli madde.** Şu an Gate 1 takvim + prompt yazıldıktan sonra geliyor; Gemini token’ı reddedilen konulara harcanıyor. | Sıradaki iş |
| 3 | Gate 2 = PUBLISH / REVISE / REJECT + feedback | Evet. Partial regeneration Prototipal tek-prompt API’sinde sınırlı; ilk sürümde REVISE = prompt’a feedback ekleyip yeniden üret. | Sonra |
| 4 | AUTO_PUBLISH gerçek enforcement | Evet — dokümanda vardı, node’da yoktu. | **Yapıldı** |
| 5 | Apify `runs/last` kullanma | Evet, gerçek bug (paralel run’da başka run’ın verisini okur). | **Yapıldı** |
| 6 | Polling limiti | Evet. `Wait1` / `Wait` döngüleri sınırsız; Apify FAILED/ABORTED olursa sonsuza kadar döner. | Sıradaki iş |
| 7 | Idempotency (`youtube_video_id` varsa dur) | Evet; upload aktif edilmeden önce şart. | Upload açılmadan önce |
| 8 | `channel_id` baştan sona | Evet ama 2. kanal gelene kadar ertelenebilir. | Sonra |
| 9 | Sheets kalsın, kolon ekle | Katılıyoruz. | Sonra |
| 10 | Kontrollü status | Evet; `database/states.py` zaten bu listeyi tanımlıyor, Sheets `durum` aynı değerleri kullanmalı. | Sonra |
| 11–12 | Ayrı analytics + basit pattern | Katılıyoruz; primary canvas’a eklenmemeli. | Sonra |
| 14 | Şimdilik parçalama | Katılıyoruz. | — |

## n8n Cloud’a özel düzeltmeler

- **`$env` Cloud’da engelli olabilir** ve Variables bu planda kapalı (API 403). Bu yüzden `DRY_RUN?` kapısı artık *fail-closed*: env okunamazsa `DRY_RUN=true`, `AUTO_PUBLISH=false` kabul edilir → upload asla yanlışlıkla çalışmaz. Gerçek yayın için bu kapıyı elle açmak gerekecek.
- **`fomat` typo** Sheets’teki gerçek kolon adı. Sadece node’da düzeltmek yazmayı bozar; önce Sheet kolonunu `format` yap, sonra mapping’i.
- **Token’ı URL’den credential’a taşıma** (madde 15): Apify token şu an sadece canlı n8n’de, git’te yok. Header Auth credential’a taşımak iyi olur.

## Bu turda yapılanlar

1. `kontrol` → `actor-runs/{basla.data.id}`; `sonuc` → `datasets/{defaultDatasetId}/items`
2. Upload yalnızca `DRY_RUN=false` **ve** `AUTO_PUBLISH=true` iken; aksi halde Telegram’a “atlandı”
3. Gemini: `gemini-2.5-flash` ve `gemini-2.0-flash` Google tarafından kapatıldı → tek seçenek `gemini-3.6-flash` + 5 retry (503 yoğunluk için)

## Önerilen sıra (review’un sırası küçük değişiklikle)

1. Polling limit + Apify FAILED dalı (ucuz, deneme sırasında takılmayı önler)
2. Gate 1 konu seçimi
3. Gate 2 üç aksiyon
4. Idempotency → sonra ilk gerçek upload
5. channel_id / multi-channel, analytics, patterns
