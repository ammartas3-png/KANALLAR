# Operatör kontrol listesi (senin yapman gerekenler)

Kod tarafındaki entegrasyonlar hazır. Aşağıdakiler **senin** hesabında / panellerinde yapılmalı.
Sırlar (API key, token) asla GitHub’a commit edilmez.

---

## 1) Zorunlu — YouTube OAuth (yükleme için)

1. Google Cloud Console’da YouTube Data API v3 (+ istenirse YouTube Analytics API) açık olsun.
2. OAuth **Desktop** client JSON’u proje kökünde `client_secret.json` olarak dursun (zaten yüklediysen tamam).
3. **Bir kez** tarayıcıda Google hesabıyla onay ver → `token.json` oluşsun.
   - Cloud agent senin Mac’inde tarayıcı açamaz; bunu kendi makinenizde veya her zaman açık bir sunucuda yapın.
4. Kontrol:
   ```bash
   python -m automation channel
   ```
   `token: true` görmelisin.

---

## 2) Video üret → izle → onayla → yükle

```bash
# Üret (varsayılan: YouTube’a yüklemez, awaiting_approval olur)
python -m automation produce

# Onay bekleyenler
python -m automation pending

# İzle (stüdyo veya content/videos/<id>/final.mp4)
python -m automation studio

# Onayla + private yükle
python -m automation approve --id <VIDEO_ID> --upload
```

Stüdyoda da **Onayla + yükle** / **Reddet** butonları var.

Onay kapısını kapatmak (önerilmez): `.env` içinde `REQUIRE_HUMAN_APPROVAL=false`  
Acil atlama: `produce --force-upload` (dikkatli kullan).

---

## 3) Opsiyonel — Kie.ai (birincil AI medya)

1. https://kie.ai hesabı aç, kredi yükle.
2. API key: https://kie.ai/api-key → `.env` `KIE_API_KEY=...`
3. Model id’lerini market’ten seç: https://kie.ai/market  
   Örnek alanlar: `KIE_DEFAULT_IMAGE_MODEL`, `KIE_DEFAULT_VIDEO_MODEL`, `KIE_DEFAULT_VOICE_MODEL`
4. Kaliteyi aç: `MEDIA_QUALITY=auto` (veya `cheap`)
5. Kontrol: `python -m automation media-status` → `kie.configured: true`

Not: V1 assembler hâlâ FFmpeg kartları kullanır; Kie seçimi plan/routing’e yazılır. Clip indirme sonraki adım.

---

## 4) Opsiyonel — Higgsfield (yedek / premium)

1. Higgsfield Cloud’dan `HF_API_KEY_ID` + `HF_API_KEY_SECRET` al.
2. Endpoint’leri docs’tan doldur: https://docs.higgsfield.ai  
   `HF_DEFAULT_IMAGE_ENDPOINT`, `HF_DEFAULT_VIDEO_ENDPOINT`, (varsa) voice.
3. `MEDIA_QUALITY=premium` veya Kie yokken auto fallback.

---

## 5) Opsiyonel — Üretim bulutu (Cursor kapalıyken çalışsın)

| Ne | Neden |
|----|--------|
| PostgreSQL (Neon/Supabase/RDS) | `DATABASE_URL` — SQLite yalnızca deneme |
| Object storage (R2/S3/GCS) | final mp4, ses, thumb kalıcı |
| Always-on worker (VM / Railway / Fly / Render) | `produce` + `analytics` zamanlayıcı |
| Secrets (env / vault) | OAuth + Kie/HF anahtarları |

n8n **zorunlu değil**; ileride yalnızca cron / Slack “onay?” bildirimi için.

---

## 6) Kontrol komutları

```bash
python -m automation media-status
python -m automation pending
python -m automation job --id <VIDEO_ID>
python -m automation analytics   # token + Analytics API gerekir
```

---

## Senin yapılacaklar (kısa)

1. [ ] `token.json` üret (OAuth bir kez)
2. [ ] `produce` çalıştır, videoyu izle
3. [ ] `approve --id … --upload` ile private Short doğrula
4. [ ] (İsteğe bağlı) Kie key + market model id’leri
5. [ ] (İsteğe bağlı) Higgsfield key + endpoint’ler
6. [ ] (İsteğe bağlı) Postgres + storage + always-on host
7. [ ] YouTube kanalının doğru Google hesabına bağlı olduğundan emin ol

Sorular / sırlar: değerleri chate yapıştırma; sadece “ekledim / eklemedim” de.
