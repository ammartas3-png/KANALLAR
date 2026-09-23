# ChatGPT Workflow Review — PRIMARY YouTube Full

**Review date:** 2026-09-23  
**Target branch:** `cursor/n8n-shorts-factory-ee45`  
**Primary workflow:** `n8n/workflows/primary/youtube-full-pipeline.json`

Bu dosya Cursor / Claude / ChatGPT için teknik review notudur. Amaç mevcut sistemi baştan yazmak değil; çalışan n8n akışını daha güvenli, ucuz, ölçeklenebilir ve öğrenen bir Shorts fabrikasına dönüştürmektir.

---

## 1. Mevcut yapıda doğru olanlar

Mevcut omurga korunmalı:

```text
Form / Schedule
→ Gemini keyword generation
→ Apify YouTube research
→ Google Sheets checkpoint/queue
→ Gemini content planning
→ Telegram Gate 1
→ SEO preflight
→ Prototipal video generation
→ async polling
→ Telegram Gate 2
→ DRY_RUN guard
→ YouTube upload
```

Özellikle şunlar iyi ve yeniden yazılmamalı:

- n8n'in ana orchestrator olması
- araştırma ve video üretiminin ayrılması
- Google Sheets'in MVP queue/checkpoint olarak kullanılması
- iki insan onay kapısı
- ücretli video üretiminin Gate 1 sonrasına bırakılması
- YouTube upload öncesi Gate 2
- `DRY_RUN=true` güvenlik kapısı
- async video job polling
- SEO preflight
- eski workflow'ların archive altında tutulması

---

## 2. En önemli değişiklik: Gate 1 daha erken olmalı

Şu an Gate 1, başlık/açıklama ve sahne promptları oluşturulduktan sonra geliyor.

Hedef akış şu olmalı:

```text
Research
→ 3–5 topic candidate
→ duplicate/history check
→ candidate ranking
→ TELEGRAM GATE 1
→ kullanıcı bir konu seçer
→ script
→ hook
→ title/description
→ scene prompts
→ media/video generation
```

Gate 1 gerçek bir **topic selection gate** olmalı; sadece hazırlanmış takvime evet/hayır demek olmamalı.

Telegram mesajında her aday için en az:

```text
TOPIC
ANGLE
HOOK
WHY THIS TOPIC
SOURCE / TREND SIGNAL
```

sunulsun.

Aksiyonlar:

```text
[1'i seç]
[2'yi seç]
[3'ü seç]
[Yeni fikirler]
```

Mümkünse opsiyonel `Feedback` de desteklensin.

---

## 3. Gate 2 üç aksiyonlu olmalı

Mevcut evet/hayır onayı genişletilmeli.

İstenen yapı:

```text
Video hazır

[PUBLISH]
[REVISE]
[REJECT]
```

`REVISE` sonrası kullanıcı metin feedback'i verebilmeli.

Örnek:

- "3. sahneyi değiştir"
- "sesi değiştir"
- "ilk 2 saniyeyi daha güçlü yap"
- "başlığı değiştir"
- "videoyu 5 saniye kısalt"

Revision mümkün olduğu kadar **partial regeneration** yapmalı.

Örnek:

```text
TITLE feedback → sadece metadata
SCENE 3 feedback → sadece scene 3 + rerender
VOICE feedback → TTS + rerender
CAPTION feedback → caption render
FULL VIDEO feedback → full regenerate
```

Böylece API maliyeti düşer.

---

## 4. AUTO_PUBLISH gerçek bir güvenlik kontrolü olmalı

Dokümanda `AUTO_PUBLISH=false` yazıyor fakat primary workflow'da aktif enforcement ayrıca doğrulanmalı.

YouTube upload için iki koşul birlikte sağlanmalı:

```text
valid human Gate 2 approval
AND
AUTO_PUBLISH=true
AND
DRY_RUN=false
```

Varsayılan:

```text
AUTO_PUBLISH=false
DRY_RUN=true
```

Bu değişkenlerden biri güvenli durumda ise upload çalışmamalı.

---

## 5. Apify `runs/last` kullanılmamalı

Primary workflow şu anda Apify tarafında `runs/last` mantığına dayanıyorsa bu multi-run / multi-channel için risklidir.

Problem:

- Channel A research job başlatır
- hemen sonra Channel B job başlatır
- Channel A `runs/last` sorunca Channel B run'ını okuyabilir

Doğru model:

```text
POST Apify run
→ run_id kaydet
→ GET /runs/{run_id}
→ tamamlanınca o run'a ait dataset_id / dataset items
```

Her execution kendi run ID'sini taşımalı.

---

## 6. Polling sınırsız olmamalı

Hem Apify hem video generation için açık retry limitleri olmalı.

Her async job için:

```text
attempt_count
max_attempts
started_at
max_wait_minutes
last_status
```

mantığı eklenmeli.

Öneri:

```text
Wait
→ status check
→ completed? yes → continue
→ failed? yes → error handler
→ timeout/max attempts? yes → error handler
→ no → backoff/wait
```

Sonsuz `Wait → Check → Wait` loop'u olmamalı.

---

## 7. Idempotency zorunlu

Bir n8n retry aynı videoyu iki kez YouTube'a yüklememeli.

Her içerik için kalıcı ID kullan:

```text
content_id
channel_id
render_job_id
youtube_video_id
status
```

Upload öncesi:

```text
if youtube_video_id exists:
    STOP / already published
```

Ayrıca aynı `content_id` için eşzamanlı iki render/upload execution engellenmeli.

---

## 8. `channel_id` akışın başından sonuna taşınmalı

Başlangıçta 2 kanal, sonra 5+ kanal hedefleniyor.

Her job'ın temel context'i:

```text
channel_id
language
niche
target_country
voice
visual_style
publish_times
daily_video_limit
template_id
llm_provider
video_provider
youtube_credential_mapping
```

Bu değerler node'larda hardcode edilmemeli.

İlk MVP Sheets üzerinden çalışabilir; ancak config tek yerde tutulmalı.

---

## 9. Google Sheets şimdilik kalabilir

MVP aşamasında hemen Postgres/Supabase'e geçmek zorunda değiliz.

Sheets'i kısa vadede job board olarak tutmak mantıklı.

Ama aşağıdaki kolonlar şimdiden eklenmeli:

```text
content_id
channel_id
research_run_id
topic_id
selected_topic
status
topic_approved_at
video_approved_at
render_job_id
youtube_video_id
published_at
revision_type
revision_feedback
```

Bu sayede ileride Supabase/Postgres migration kolaylaşır.

---

## 10. Status / state machine netleştirilmeli

Serbest metin yerine mümkün olduğunca kontrollü status kullan.

Örnek:

```text
RESEARCHING
IDEAS_READY
TOPIC_PENDING_APPROVAL
TOPIC_APPROVED
TOPIC_REJECTED
SCRIPT_READY
MEDIA_GENERATING
VIDEO_READY
VIDEO_PENDING_APPROVAL
VIDEO_REVISION_REQUESTED
VIDEO_APPROVED
READY_TO_PUBLISH
PUBLISHED
FAILED
```

Workflow hangi aşamada kaldığını execution history'den tahmin etmek zorunda kalmamalı.

---

## 11. Analytics ayrı workflow olmalı

Primary workflow'u daha da büyütme.

Upload sonrası analytics ayrı scheduled workflow olarak çalışsın.

Öneri:

```text
PUBLISHED VIDEO
→ 6h snapshot
→ 24h snapshot
→ 72h snapshot
→ 7d snapshot
```

YouTube API'den erişilebilen metrikler çekilsin.

Amaç sadece dashboard değil; sonraki içerik kararlarını iyileştirmek.

---

## 12. Content learning katmanı basit başlamalı

İlk sürümde ağır autonomous agent kurma.

Her kanal için özet pattern üret:

```text
winning_topics
winning_hooks
bad_hooks
best_durations
best_publish_windows
best_templates
best_visual_styles
```

Yeni research/script çağrısında tüm geçmiş database'i LLM'e verme.

Sadece ilgili kanal için küçük bir özet context ver.

Bu token maliyetini düşürür.

---

## 13. Development memory ile content memory ayrılmalı

### Development memory

Cursor / Claude / ChatGPT için:

```text
AGENTS.md
docs/AKIS.md
docs/PROJECT_STATE.md
docs/ARCHITECTURE.md
docs/DECISIONS.md
```

### Content memory

YouTube sistemi için:

```text
channels
topics
videos
human feedback
analytics
experiments
patterns
```

İkisini birbirine karıştırma.

---

## 14. Primary workflow'u şimdilik parçalamak zorunlu değil

Tek canvas şu anda insan tarafından okunabiliyor ve MVP için kabul edilebilir.

Sırf mimari olarak güzel görünsün diye hemen 10 subworkflow'a bölme.

Ancak büyüdüğünde doğal sınırlar şunlar olabilir:

```text
01 research
02 topic approval
03 script / scenes
04 media generation
05 video approval
06 publish
07 analytics
08 error handler
```

Önce çalışır ve güvenli hale getir; sonra modülerleştir.

---

## 15. Küçük fakat kontrol edilmesi gereken teknik noktalar

Cursor özellikle şunları doğrulasın:

- `format` alanında typo (`fomat`) var mı?
- long/short branching gerçekten doğru mu?
- Telegram reject branch'leri doğru status yazıyor mu?
- Prototipal failed/cancelled status handling var mı?
- Apify failed/aborted/timed-out status handling var mı?
- `retryOnFail` limitsiz davranıyor mu?
- duplicate YouTube upload engelleniyor mu?
- credential değerleri workflow JSON içine sızmış mı?
- HTTP node'larında API token URL query parametresi yerine credential/header kullanmak mümkün mü?
- production `DRY_RUN` ve `AUTO_PUBLISH` değişkenleri gerçekten n8n environment/variables üzerinden geliyor mu?

---

# Önerilen hedef akış

```text
FORM / SCHEDULE
      ↓
CHANNEL CONFIG
      ↓
YouTube / trend research
      ↓
Duplicate + history check
      ↓
3–5 TOPIC CANDIDATES
      ↓
┌─────────────────────────┐
│ GATE 1 — TELEGRAM       │
│ 1 / 2 / 3 / NEW IDEAS  │
└────────────┬────────────┘
             ↓
       SELECTED TOPIC
             ↓
       Script + Hook
             ↓
         Script QC
             ↓
       Scene Planning
             ↓
      Video Generation
             ↓
 retry / timeout / QC
             ↓
┌─────────────────────────┐
│ GATE 2 — TELEGRAM       │
│ PUBLISH / REVISE / REJECT│
└────────────┬────────────┘
             ↓
 AUTO_PUBLISH + DRY_RUN
             ↓
       YouTube Upload
             ↓
          Analytics
             ↓
       Content Patterns
             ↓
       Next Research
```

---

# Cursor için öncelik sırası

Mevcut sistemi baştan yazma.

Şu sırayla ilerle:

1. Gate 1'i gerçek topic-selection gate haline getir.
2. Apify run-specific ID kullanımını düzelt.
3. Async polling timeout / max-attempt ekle.
4. Gate 2'yi PUBLISH / REVISE / REJECT + feedback yap.
5. Gerçek `AUTO_PUBLISH` enforcement ekle.
6. `content_id` / `channel_id` / idempotency ekle.
7. Multi-channel config katmanı oluştur.
8. Ayrı analytics workflow ekle.
9. Basit content-pattern learning ekle.
10. Sistem stabil olduktan sonra gerekirse Supabase/Postgres'e migrate et.

Her adım sonrası:

```text
- workflow validation
- DRY_RUN smoke test
- PROJECT_STATE.md update
- commit
```

Gerçek YouTube upload veya ücretli video generation testleri kullanıcı açıkça izin vermeden yapılmamalı.
