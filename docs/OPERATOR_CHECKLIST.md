# Operatör kontrol listesi — cloud-first (Mac local yok)

Kod cloud worker olarak çalışır. Laptop’ta kurulum **gerekmez**.
Detay: [CLOUD_DEPLOY.md](CLOUD_DEPLOY.md)

Sırları asla GitHub’a veya chate yapıştırma.

---

## Senin yapman gerekenler (sadece paneller / tarayıcı)

### 1) Hosting (zorunlu — Cursor kapalıyken üretim için)
1. Railway / Fly / Render / herhangi bir VM
2. Bu repoyu deploy et (`Dockerfile` veya `docker compose`)
3. Açık port **8080** → Studio + `/health`

### 2) Postgres (zorunlu production)
1. Neon/Supabase/RDS veya compose `db`
2. Secret: `DATABASE_URL=postgresql+psycopg://...`

### 3) YouTube (yükleme için)
1. Google Cloud’da YouTube Data API (+ Analytics) açık
2. OAuth client JSON → secret `YOUTUBE_CLIENT_SECRETS_JSON`
3. Bir kez token al → secret `YOUTUBE_TOKEN_JSON`  
   (Mac şart değil; geçici VM veya daha önce alınmış token)

### 4) Onay (her gün)
1. Tarayıcıda `https://<worker-host>/`
2. Videoyu izle → **Onayla + yükle** veya **Reddet**
3. Private Short kanalda görünsün

### 5) Opsiyonel
| Secret | Ne |
|--------|-----|
| `STORAGE_BACKEND=s3` + R2/S3 keys | Kalıcı preview |
| `KIE_API_KEY` + model id | AI medya |
| `HF_API_KEY_ID` / `HF_API_KEY_SECRET` | Premium fallback |
| `WORKER_PRODUCE_CRON` | Üretim saati (UTC) |

---

## Kontrol (sunucuda veya GitHub Actions — Mac değil)

```bash
curl https://<host>/health
# veya container içinde:
python -m automation storage-status
python -m automation media-status
python -m automation pending
```

---

## Kısa checklist

1. [ ] Cloud host deploy
2. [ ] `DATABASE_URL`
3. [ ] `YOUTUBE_CLIENT_SECRETS_JSON` + `YOUTUBE_TOKEN_JSON`
4. [ ] `/health` → ok
5. [ ] Studio’dan 1 video onayla
6. [ ] (İsteğe) R2/S3
7. [ ] (İsteğe) Kie/HF

Local `pip install` / Mac terminal **bu listede yok**.
