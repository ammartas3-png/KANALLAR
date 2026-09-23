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
| Gemini (3.5-flash) | ✅ |
| Apify (run ID, sınırlı bekleme) | ✅ ~0,20 $ / tur |
| Sheets | ✅ operatöre ait `KANALLAR analizler` / `KANALLAR icerik-takvim` |
| 3 aday konu | ✅ üretildi |
| Gate 1 Telegram | ⛔ bot bu chat’i tanımıyor (`8715342169` botu hiç başlatmamış, `1240141730` deaktif hesap). Geçici `TEMP telegram chat-id capture` workflow’u açık: n8n’deki bota herhangi bir mesaj at → chat id otomatik yakalanır |
| Video | ⛔ Prototipal Bearer boş. Sora 2 API 24 Eylül 2026’da kapanıyor, alternatif değil. Gerekli: Prototipal token veya Kie.ai anahtarı |
| YouTube | ✅ bağlı tek hesap: `YouTube account 3` → kanal **TAŞDEMiR MA (@tasdemirma3215)** |
