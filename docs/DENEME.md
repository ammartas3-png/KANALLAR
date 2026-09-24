# Denemelik 1 Short — nasıl çalıştırılır

## Form (workflow aktif)

https://ammartd20.app.n8n.cloud/form/ccbd8f46-1dfd-4b1c-ac08-450c6f229154

Örnek doldurma:
- **Konu:** `Osmanlı padişahları kısa bilgi`
- **Hafta Sayısı:** `1` (şu an yok sayılıyor — **sadece 1 Short** üretilir)
- **İçerik Dili:** `tr`

Sonra Telegram’da (`8715342169`) Gate1 onayını bekle.

## Şu an hazır olanlar

- Workflow **aktif:** `PRIMARY: YouTube Full (sade)`
- Gemini + Sheets + Telegram credential bağlı
- Sheets append node’ları bağlandı
- Deneme modu: **0 long + 1 short**
- `DRY_RUN` default → YouTube’a **yüklemez** (video üretilebilir, publish yok)

## Senin doldurman gereken (yoksa akış kırılır)

n8n’de şu HTTP node’larda boş bırakılmış alanlar:

| Node | Ne eksik |
|------|----------|
| `basla` / `kontrol` / `sonuc` | Apify URL sonundaki `token=` |
| `olustur` / `video-kontrol` | Header `Authorization: Bearer <PROTOTIPAL_TOKEN>` |

Bunları n8n UI’dan bir kez yapıştır → Save.

## Beklenen sıra

1. Form submit  
2. Apify + Gemini + Sheets  
3. Telegram: takvim/konu onay (Approve)  
4. SEO OK → Prototipal video  
5. Telegram: video onay  
6. `DRY_RUN` → “upload atlandı” mesajı (normal)

YouTube’a gerçek deneme için sonra `DRY_RUN=false` + YouTube credential (bağlandı).

## Bilinen hatalar

| Hata | Çözüm |
|------|--------|
| `anahtar-kelimeler` → resource not found | Gemini model eskiydi; tüm node’lar `models/gemini-3.6-flash` yapıldı. Formu tekrar çalıştır. |
| Apify 401 | `basla`/`kontrol`/`sonuc` URL’de `token=` doldur |
| Prototipal 401 | `olustur`/`video-kontrol` Bearer doldur |

Normal üretime dönmek için `icerik-fikir-baslik-aciklama` prompt’undaki  
`Uzun format sayısı: 0` / `Shorts sayısı: 1` satırlarını tekrar `hafta` / `hafta*2` yap.


## İlk tur (Fatih Sultan Mehmed, en) — 2026-09-23 durumu

| Aşama | Durum |
|-------|-------|
| Form / haftalık tetik | ✅ |
| LLM | ✅ OpenAI `gpt-4.1-mini` (Gemini ücretsiz kota günde 20 istek/model, yetmedi) |
| Apify (run ID, sınırlı bekleme) | ✅ ~0,20 $ / tur |
| Sheets | ✅ operatöre ait `KANALLAR analizler` / `KANALLAR icerik-takvim` |
| 3 aday konu | ✅ üretildi |
| Gate 1 Telegram | ✅ yeni bot `@Yt_ammar_bot` (n8n credential `Telegram Yt_ammar_bot`), chat `8715342169` |
| Video | ✅ Kie.ai Veo 3.1 (`veo3_fast`, 9:16, 8 sn, sesli) — anahtar canlı n8n’de, git’te yok. Bakiye 80 kredi ≈ 1 video; REVISE için kredi yüklemek gerekir |
| YouTube | ✅ bağlı tek hesap: `YouTube account 3` → kanal **TAŞDEMiR MA (@tasdemirma3215)** |

### Kie / Veo notları (ilk video)
- Veo, gerçek/tarihi ünlü kişileri engeller (`prominent public figure`). İsim çıkarmak yetmedi; `olustur` prompt’u artık hükümdar adlarını/unvanlarını ve şehir/yılı nötrler, lideri anonim ve arkadan gösterir. Başarısız denemeler kredi yakmaz.
- İlk başarılı render: `veo3_fast` 60 kredi. Kalan bakiye 20 → bir sonraki video / REVISE için Kie kredisi yükle.
- Üretimi araştırmasız yeniden tetiklemek için gizli yollu `uretim-tetik` webhook’u var (yol repo’da `<secret>`).
- Durum: execution 1438 Gate 2’de; video Telegram’a gönderildi.

### Gate 2 → YouTube (2026-09-23 13:23 UTC)
- Operatör **PUBLISH** seçti; `Upload a video` YouTube’dan `429 Video Uploads per day` aldı (Google Cloud projesi `498586711441`, YouTube account 3).
- Kota 07:00 UTC’de sıfırlanır; yeniden deneme planlandı (önce execution 1438 retry, olmazsa yedek MP4 ile yükleme).
- MP4 yedeği agent deposunda (720×1280, 8 sn, sesli) — Kie geçici linki silinse bile kaybolmaz.
- Not: 2020 sonrası oluşturulan ve YouTube denetiminden geçmemiş API projelerinden yüklenen videolar YouTube tarafından *private* kilitlenebilir. Tekrar olursa Cloud Console → YouTube Data API v3 → Quotas / audit kontrol edilmeli.
- Kanal kontrolü (YouTube node, 13:45 UTC): TAŞDEMiR MA public, `longUploadsStatus=eligible`, 0 public video. Kotayı dolduran yükleme: 2026-09-22 19:43 UTC `KANALLAR pipeline test - flash test` (private, eski test). Proje limiti muhtemelen ~1 upload / 24 saat → ek deneme 19:50 UTC.
- 16:00 UTC Schedule, render edilmiş ama yüklenmemiş satırı (`beklemede`) tekrar render etmeye çalıştı; Kie 402 (yetersiz kredi) ile durdu, kredi harcanmadı. Düzeltme: render biter bitmez satır `video-hazir` olur.
- 19:48 UTC: execution 1438 API ile başarısız node’dan retry edildi (1443) → yine `429 Video Uploads per day`. Kayan 24 saat hipotezi yanlış; sonraki deneme 07:15 UTC (kota sıfırlandıktan sonra). Yine olursa proje limitine Cloud Console’dan bakılmalı.

### ✅ Yayında (2026-09-24 07:15 UTC)
- Execution 1438, kota sıfırlandıktan sonra API ile başarısız node’dan retry edildi (1444) → upload başarılı, Sheets `yayinlandi`.
- https://youtube.com/shorts/Ok1KeDvXY3s — `privacyStatus=public`, `madeForKids=false`, işlendi (9 sn).
- Proje limiti günde ~1 upload gibi davranıyor (sayım Pasifik gece yarısı sıfırlanıyor); haftalık seri için yeterli, test yüklemelerinden kaçınılmalı.
