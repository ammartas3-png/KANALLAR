# Kanallar

Tek kanallı YouTube Shorts fabrikası. OpenMontage akışını (research → idea → script → assets → voice → captions → render → QA) yerelde, düşük maliyetle çalıştırır.

**MVP kanalı:** `channels/channel_01` — Bilim Dakikası (TR, 9:16). İkinci kanala geçilmez; çekirdek ısınana kadar tek hat.

## Ne çalışır

```
Research → Idea → Script → Assets → Voice → Video + Captions → QA → (opsiyonel Upload) → Analytics → Director
```

- Katalog + Wikipedia özet/most-read trend + `yt-dlp` metadata (indirme yok)
- Orijinal senaryo JSON (`hook`, `scenes`, `cta`, `estimated_duration`)
- TTS: edge-tts → gTTS → espeak-ng
- FFmpeg: slayt, zoom/pan, ses normalize, ASS altyazı, 1080×1920 encode
- Remotion şablonu: `apps/remotion` (HOOK → 3 sahne → CTA). Varsayılan renderer FFmpeg ($0)
- QA: çözünürlük, 9:16, süre, ses, caption, dosya boyutu
- YouTube Data API v3 yükleme (private). Analytics API hazır, credential isteğe bağlı
- PostgreSQL şeması `database/schema.sql` + `scripts/bootstrap_db.sh` — CI/SQLite fallback
- Agent log + `cost_per_video`
- Basit stüdyo: `python3 -m automation studio`

## Kurulum

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
bash scripts/bootstrap_db.sh
# .env içinde DATABASE_URL postgres satırını aç
cd apps/remotion && npm install && cd ../..
python3 -m automation channel
python3 -m automation produce --topic ahtapot-uc-kalp
python3 -m automation studio --host 127.0.0.1 --port 8080
```

Ortam: Python 3.11+, Node 20+, FFmpeg.

Eski CLI hâlâ durur: `python3 -m kanallar produce bilim-dakikasi`.

## YouTube

1. YouTube Data API v3 + OAuth masaüstü istemcisi
2. `client_secret.json`
3. `python3 -m automation produce --upload` — video **private** gider

Browser ile Studio’ya tıklamak yok. Resmi API yoksa üretim yerel kalır.

## Bilinçli olarak sonraya bırakılanlar

OpenViking, browser-use (sadece `research/browser.py` soyutlama), n8n, Redis, LangGraph, Kubernetes, Ruflo, swarm, ücretli AI video. Codebase Memory MCP isteğe bağlı; yerel indeks: `python3 scripts/index_codebase.py`.

## Test

```bash
pytest -q
```
