# Cloud deploy — Mac/local kurulum yok

Bu sistem **cloud worker** olarak çalışmak üzere tasarlandı. Laptop’ta `pip install` / OAuth server şart değil.

## Mimari

```
[Docker / Railway / Fly / Render / VM]
   worker (= studio :8080 + günlük produce + analytics)
        │
        ├── Postgres (managed veya compose `db`)
        ├── Object storage (R2/S3) — opsiyonel ama önerilir
        └── Secrets (platform env)
              YOUTUBE_*_JSON, KIE_*, HF_*, DATABASE_URL, STORAGE_*
```

## Hızlı yol: Docker Compose (bir sunucuda)

1. Repoyu sunucuya clone et (veya GitHub deploy).
2. Platform secret’larına şunları koy (değerleri chate yazma):
   - `YOUTUBE_CLIENT_SECRETS_JSON` — OAuth client JSON (ham veya base64)
   - `YOUTUBE_TOKEN_JSON` — bir kez alınmış refresh token JSON
   - İleride: `STORAGE_*`, `KIE_API_KEY`, …
3. Çalıştır:
   ```bash
   docker compose up -d --build
   curl https://<host>/health
   ```
4. Studio: `https://<host>/` — izle / onayla / reddet  
5. Worker her gün UTC 08:00’de `produce` eder (`WORKER_PRODUCE_CRON`).

## YouTube token’ı Mac olmadan nasıl?

Seçenekler:
1. **Cursor Cloud Agent** ortamında bir kez OAuth (agent tarayıcı/flow destekliyorsa).
2. **Geçici küçük VM**’de tek sefer `InstalledAppFlow` → çıkan `token.json` içeriğini `YOUTUBE_TOKEN_JSON` secret’ına yapıştır → VM’i kapat.
3. Daha önce alınmış token varsa sadece secret’a koy.

Dosyayı Mac’e kopyalamana gerek yok; worker boot’ta env’den dosyaya yazar (`python -m automation bootstrap`).

## Managed Postgres

Neon / Supabase / RDS → `DATABASE_URL=postgresql+psycopg://...`  
Compose içindeki `db` yerine bunu kullan, `db` servisini kaldır.

## Object storage (R2 örneği)

```
STORAGE_BACKEND=s3
STORAGE_BUCKET=kanallar
STORAGE_ACCESS_KEY=...
STORAGE_SECRET_KEY=...
STORAGE_ENDPOINT=https://<accountid>.r2.cloudflarestorage.com
STORAGE_PUBLIC_BASE_URL=https://media.example.com
```

Produce sonrası `final.mp4` bucket’a gider; `preview_url` döner.

## Tek komut entrypoint

```bash
python -m automation.worker
# veya
python -m automation worker
```

Health: `GET /health`

## Senin tarayıcıdan yapacakların

1. Hosting hesabı (Railway/Fly/Render/VM) + deploy  
2. Secret’ları panelden ekle  
3. `/` üzerinden onay  
4. (Opsiyonel) R2/S3 + Kie key  

**Mac’te proje çalıştırmana gerek yok.**
