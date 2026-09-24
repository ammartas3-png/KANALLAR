# CHANNELS_STATUS.md — YouTube kanal durumu ve Cursor için talimatlar

Son güncelleme: 2026-09-24 · Hazırlayan: Claude (Cowork), YouTube Studio'da elle kontrol edildi.
Repoya aktaran: Cursor (Claude'un oturumunun yazma izni yoktu; içerik Google Doc'tan birebir alındı).

Okuyan agent (Cursor): Bu dosya, `n8n/` akışı ve upload kodu için bağlayıcı kurallar içerir. Aşağıdaki "Cursor görevleri" bölümünü uygula.

---

## 0. KESİN KURAL — Kişisel kanala hiçbir şey yayınlanmaz

| Kişisel kanal | Kural |
|---|---|
| TAŞDEMİR MA · @tasdemirma3215 · `UCa-ulc77JRueoWa11LPQUVg` | Bu kanala hiçbir video yüklenmez (gizli test dahil). Upload kodu bu ID'yi hard-block etmeli. |

Mevcut `token.json` (`~/kanallar-oauth/token.json`, worker'da `YOUTUBE_TOKEN_JSON`) bu kişisel kanal için alınmış. Bu yüzden şu an sistem her şeyi kişisel kanala yüklüyor. Bu token ile upload yapılmamalı.

### Kişisel kanalda yanlışlıkla yayınlananlar (2026-09-24 itibarıyla)

| Video | Durum | Not |
|---|---|---|
| "Fatih's Genius Battle Plan 🎯" (Short, 0:09) | Herkese açık, 24 Eyl 2026, 116 izlenme | Tarih içeriği → doğru yeri History in a Minute. YouTube otomatik "yapay zekâ etiketi" koymuş. Kaldırma/gizleme kararı kullanıcıda. |
| "KANALLAR pipeline test - flash test" (0:03) | Gizli, 22 Eyl 2026 | Test videosu. |

---

## 1. Açılan kanallar (hepsi aynı Google hesabı altında Brand Account)

Strateji: İngilizce içerik, Tier-1 izleyici (ABD/İngiltere/Avrupa), ortak marka ailesi "… in a Minute".

| Kanal | Handle | Channel ID | Durum | Niş | Upload kategori |
|---|---|---|---|---|---|
| Money in a Minute | @MoneyInAMinuteShorts | `UCj6vC105nA-2P627Q01cIgw` | ✅ Açık, ayarlı, marka yayında | Kişisel finans eğitimi (yatırım tavsiyesi değil) | Eğitim (27) |
| Science in a Minute | @ScienceInAMinuteHQ | `UCjmDhWo0I7KIPKVTDBZZbqg` | ✅ Açık (2026-09-24) | Bilim & uzay | Bilim ve Teknoloji (28) |
| History in a Minute | @HistoryInAMinuteShorts | `UCDn9Qz6jZ_ikwm37yuD4NOg` | ✅ Açık (2026-09-24) | Tarih hikâyeleri | Eğitim (27) |

Üç kanal da açık; ID'ler `channels/*/config.yaml` içinde.

### Money in a Minute — YouTube Studio'da yapılan ayarlar

- İkamet edilen ülke: Türkiye (yasal zorunluluk; hedef kitle ülkesi DEĞİL — gelir izleyici ülkesine göre hesaplanır)
- Kitle: Çocuklara özel değil (`selfDeclaredMadeForKids=false`)
- Kanal anahtar kelimeleri: personal finance, money tips, financial literacy, budgeting, credit score, compound interest, saving money, money in a minute
- Yükleme varsayılanları: Görünürlük Gizli, kategori Eğitim, video dili İngilizce, başlık/açıklama dili İngilizce, etiketler yukarıdakilerle aynı + shorts
- Profil resmi, banner, video filigranı, İngilizce açıklama (+ "not financial advice" uyarısı) yayında
- Özellik uygunluğu: Standart ✅ · Orta seviye (özel küçük resim, 15 dk+) ⏳ kimlik onayı bekliyor → onaylanana kadar `thumbnails.set` 403 verir
- İletişim e-postası: boş (kullanıcı iş e-postası belirleyecek)

### Marka varlıkları

Kullanıcının Mac'inde: `~/Pictures/Kanal Marka/` → `{money,science,history}_{logo,banner,watermark}.png`

Renkler: Money `#22C55E` · Science `#38BDF8` · History `#F5B142` · Arka plan `#0B1220` · Metin `#F4F1E8`

### Para kazanma (YPP) durumu

Hiçbir kanalda açık değil. Studio'daki "Gelir elde etmeye başlayın" ekranı sadece uygunluk sayfası.

- Erken aşama (üyelik/Supers/alışveriş): 500 abone + son 90 günde 3 video + (3.000 saat izlenme veya 90 günde 3M Shorts izlenmesi)
- Reklam geliri (Shorts Akışı reklamları dahil): 1.000 abone + (4.000 saat veya 90 günde 10M Shorts izlenmesi)
- Kişisel kanalın bu hedefe sayılması istenmiyor; tüm büyüme yeni kanallarda olmalı.

---

## 2. Cursor görevleri (öncelik sırasıyla)

### G1 — Kanal kaydı + kişisel kanal kilidi (ÖNCE BU)

1. `channels/` altında kanal başına config: `money_in_a_minute`, `science_in_a_minute`, `history_in_a_minute`. Her birinde:
   - `youtube_channel_id` (yukarıdaki tablo; henüz olmayanlar boş → upload devre dışı)
   - `language: en`, İngilizce ses (ör. edge-tts `en-US-GuyNeural` / `en-US-AriaNeural`), İngilizce prompt/CTA/footer
   - `upload.category_id` (Money/History 27, Science 28), `privacy: private`, `made_for_kids: false`, `default_language: en`
   - marka renkleri (yukarıda)
2. Kanal başına ayrı OAuth token: `YOUTUBE_TOKEN_JSON__<CHANNEL_KEY>` (veya `tokens/<channel_key>.json`). OAuth akışında Google hesap seçiminde ilgili Brand kanal seçilmeli.
3. Upload öncesi zorunlu doğrulama: `youtube.channels().list(part="id", mine=True)` → dönen ID, config'teki `youtube_channel_id` ile eşit değilse upload iptal + hata logu.
4. Hard-block: `BLOCKED_CHANNEL_IDS = {"UCa-ulc77JRueoWa11LPQUVg"}` — bu ID'ye asla upload yok (test dahil). Birim testi yaz.
5. Mevcut kişisel `token.json` worker secret'larından kaldırılsın / sadece okuma (analytics) için bile kullanılmasın.

### G2 — n8n akışını düzelt (`n8n/kanallar-cloud-orchestration.json`)

- Tek `/api/produce` çağrısı yerine kanal başına tetikleme: `POST /api/produce?channel=<key>` (Money / Science / History), her kanal farklı saat (ABD prime-time, ör. 14:00, 17:00, 20:00 UTC).
- Sadece `youtube_channel_id` dolu ve token'ı olan kanalları tetikle (worker `/api/channels` → `{key, enabled, token_ok, channel_id_verified}` dönsün).
- Yükleme her zaman insan onayından sonra (`REQUIRE_HUMAN_APPROVAL=true`): n8n Telegram/WhatsApp'a "X video onay bekliyor" + onay linki gönderir; onay → worker approve → upload.
- n8n'de YouTube node'u kullanılmaz; OAuth sadece worker'da.
- Hata/uyarı bildirimi: upload reddedilirse (kanal ID uyuşmazlığı, 403 thumbnail vb.) mesaj at.

### G3 — Kod hataları (önceki incelemede bulundu, cloud-first-worker dalında hâlâ var)

1. `youtube/api.py`: thumbnail 403 olursa video YouTube'da kalıyor ama `youtube_id` DB'ye yazılmıyor → video yüklenir yüklenmez ID'yi kaydet, thumbnail hatasını ayrı yakala (kimlik onayı gelene kadar thumbnail adımını atla).
2. `video/compose.py`: altyazı burn-in başarısız olursa sessizce altyazısız render → QA geçiyor. Fallback olursa QA `captions_burned=false` ile fail etsin.
3. `youtube/analytics.py`: `annotationClickThroughRate` metriğini kaldır; `dimensions=video` kullanılacaksa sort/maxResults ekle ya da filtreyle dimension'sız sorgula. Hataları yutma, logla.
4. Director: `avg >= 1` "win" eşiği anlamsız; kanal medyanına göre göreli skor kullan.
5. `database/session.py`: her oturumda yeni engine → engine'i modül seviyesinde cache'le (Postgres bağlantı sızıntısı).
6. `channel.upload.schedule_hour` / `frequency_per_day` kullanılmıyor; `publishAt` hiç çağrılmıyor → config'ten bağla.
7. QA `copyright_safe=True` sabit → en azından kaynak lisans kontrolü.
8. Stüdyo `/api/produce` thread hatalarını job kaydına yaz.

### G4 — Politika/kalite

- Her upload'da sentetik içerik beyanı: `status.containsSyntheticMedia = true` (AI ses/görsel kullanılıyor).
- Shorts süresi hedefi 20–45 sn (şu anki 9 sn'lik video çok kısa).
- YouTube "seri üretilmiş/tekrarlayan içerik" kuralı (Temmuz 2025) → her videoda özgün senaryo, çeşitli görsel; aynı şablonu birebir tekrarlama.
- Telifli dizi/film görüntüsü, müziği, karakteri kullanılmaz (ör. TRT "Kuruluş Osmancık" gibi dizilerin olay örgüsü sahne sahne uyarlanmaz; tarih kroniklerinden özgün senaryo yazılır).

---

## 3. Açık kararlar (kullanıcı)

- Kişisel kanaldaki "Fatih's Genius Battle Plan" videosu: gizle / kaldır / bırak.
- Money kanalı iletişim e-postası.
- Science & History kanalları: kimlik onayı gelince açılacak (Claude açacak ve bu dosyayı güncelleyecek).

---

## 4. Cursor durumu (2026-09-24)

| Görev | Durum | Nerede |
|---|---|---|
| Kural 0 — kişisel kanal kilidi (canlı n8n) | ✅ Kişisel kanal credential'ı (`YouTube account 3`) workflow'dan çıkarıldı. Upload'dan hemen önce `kanal-dogrula` → `kanal-kontrol` → `kanal-ok?`: yetkili kanal ID'si `HEDEF_KANAL_ID` ile birebir eşleşmeli ve engelli listede olmamalı; aksi halde Telegram'a `⛔` uyarısı. Haftalık Fatih turu durduruldu. | `n8n/scripts/apply_channel_guard.py` |
| Kural 0 — worker kodu | ✅ `youtube/guard.py` `BLOCKED_CHANNEL_IDS`; her yazma işleminden önce `channels.list(mine=True)` doğrulaması; eski `kanallar/youtube_upload.py` de korumalı | `youtube/api.py`, testler `tests/test_channel_guard.py` |
| G1.1 kanal config'leri | ✅ `channels/money_in_a_minute`, `science_in_a_minute`, `history_in_a_minute` (en, 27/28/27, marka renkleri, 14/17/20 UTC, başlangıç kataloğu). Science/History ID boş → upload kapalı | `channels/*/config.yaml` |
| G1.2 kanal başına token | ✅ `tokens/<channel_key>.json` veya `YOUTUBE_TOKEN_JSON__<CHANNEL_KEY>`; eski tek `YOUTUBE_TOKEN_JSON` yok sayılıyor (uyarı loglanır) | `automation/bootstrap.py` |
| G1.3 / G1.4 doğrulama + hard-block + birim testi | ✅ | `tests/test_channel_guard.py` |
| G1.5 kişisel token'ı secret'lardan kaldır | ✅ repo tarafında (`.env.example`, `docker-compose.yml`). Worker hiçbir yerde deploy edilmediği için silinecek canlı secret yok | — |
| G2 n8n | ⚠️ Farklı uygulandı, aşağıya bak | — |
| G3.1–G3.8 | ✅ thumbnail 403 ayrı yakalanıyor ve video ID kaydediliyor · altyazı fallback'inde QA `captions_burned=false` ile fail · analytics metriği ve dimension düzeltildi, hatalar loglanıyor · director kanal medyanına göre göreli skor · engine cache · `schedule_publish` açılırsa `publishAt` · QA lisans kontrolü · Stüdyo thread hataları `errors` tablosuna | ilgili dosyalar |
| G4 `containsSyntheticMedia` | ✅ worker upload'unda. ⚠️ n8n'in YouTube node'unda bu alan yok → n8n ile yüklenen videolarda Studio'dan elle işaretlenmeli (YouTube kişisel kanaldaki videoya otomatik etiket koymuş) | — |
| G4 süre 20–45 sn, özgün senaryo | ⏳ Yeni üretim akışıyla (senaryo onayı → görsel onayı → çok sahneli video + seslendirme + altyazı) gelecek | — |

### G2 neden farklı

Belge `n8n/kanallar-cloud-orchestration.json` + Python worker yolunu varsayıyor. Bu yol (`n8n/archive/`) hiçbir sunucuda çalışmıyor; canlı ve tek çalışan sistem n8n Cloud'daki `PRIMARY: YouTube Full (sade)` workflow'u (araştırma → Gate 1 → Kie video → Gate 2 → YouTube node). Bu yüzden:

- OAuth şimdilik n8n'de, **kanal başına ayrı YouTube credential** olarak (credential açılırken Google ekranında ilgili Brand kanal seçilir).
- Kanal kilidi n8n'e eklendi (yukarıda); worker deploy edilirse aynı kural `youtube/guard.py` ile zaten geçerli.
- `POST /api/produce?channel=<key>` ve `GET /api/channels` (`key, enabled, token_ok, channel_id_verified`) worker'a eklendi; worker deploy edildiğinde n8n bunlara geçebilir.

### Kullanıcıdan beklenenler

1. ~~Science & History channel ID'leri~~ ✅ eklendi (2026-09-24). n8n hedefi History in a Minute olarak ayarlandı.
2. n8n → Credentials → YouTube OAuth2 → Google ekranında **ilgili Brand kanalı** seçilerek kanal başına bağlantı (ör. `YouTube History in a Minute`). Fatih serisi History kanalına gidecek.
3. Kişisel kanaldaki Fatih videosu için karar (gizle / kaldır / bırak).
