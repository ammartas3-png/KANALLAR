# n8n — sadece orkestrasyon (üretim beyni değil)

## Önemli: YouTube n8n’den “daha kolay” bağlanmaz

Mac’te OAuth **zaten bitti** (`token.json` geçerli, kanal **TAŞDEMiR MA**).

n8n YouTube node’u **ayrı bir OAuth** ister → aynı Google consent, ikinci credential, karışıklık.  
**Yapma.** YouTube yükleme **Kanallar worker** üzerinde kalsın (`YOUTUBE_TOKEN_JSON`).

n8n’in doğru işi:
- günde bir kez worker’ı dürtmek (`/api/produce`)
- onay bekleyenleri hatırlatmak (Telegram/Slack)
- (isteğe) analytics tetiklemek

Video üretimi, QA, MediaProvider, YouTube upload → **app/worker**.

```
n8n (cron / bildirim)
   │  HTTP
   ▼
Kanallar cloud worker (:8080)
   ├── produce / pending / approve
   └── YouTube API (senin token)
```

---

## Kurulum sırası

### 1) Worker ayakta olmalı (önce bu)
Deploy + secret:
- `YOUTUBE_CLIENT_SECRETS_JSON`
- `YOUTUBE_TOKEN_JSON` ← Mac `~/kanallar-oauth/token.json`
- `DATABASE_URL`

Kontrol: `https://<worker>/health` → `"ok": true` ve youtube token true.

### 2) n8n Cloud veya self-host
1. [n8n.io](https://n8n.io) hesap / instance  
2. **Workflows → Import from File**  
3. Bu dosyayı seç: `n8n/kanallar-cloud-orchestration.json`

### 3) Ortam değişkeni
n8n’de Variables / env:

```
KANALLAR_BASE_URL=https://<senin-worker-adresin>
```

(Sonda `/` olmasın.)

### 4) İsteğe Telegram / Slack
Import’tan sonra “Format notify text” node’unun arkasına Telegram/Slack ekle → `{{$json.message}}`.

### 5) Active et
Schedule: her gün **08:00 UTC** (değiştirebilirsin).

---

## Ne import ediliyor?

| Adım | Ne |
|------|-----|
| Cron | 08:00 UTC |
| GET `/health` | Worker ayakta mı |
| POST `/api/produce` | Üretimi başlat |
| Wait ~3 dk | Render bitsin |
| GET `/api/pending` | Onay listesi |
| Mesaj metni | Studio linki |

Onay hâlâ **Studio’da** (telefon/Dell tarayıcı) veya worker CLI `approve`.

---

## Yapılmayacaklar

- n8n içinde script/video üretmek  
- n8n YouTube Upload node ile ikinci OAuth  
- AgentTube / başka repo’yu n8n’e gömmek  

---

## Senin checklist

1. [ ] Mac token → worker secret  
2. [ ] Worker deploy + `/health`  
3. [ ] n8n’e JSON import  
4. [ ] `KANALLAR_BASE_URL`  
5. [ ] (İsteğe) Telegram bildirimi  
6. [ ] Workflow Active  

Worker URL’in yoksa önce deploy; n8n tek başına YouTube’a video yükletmez.
