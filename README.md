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
- QA: çözünürlük, 9:16, süre, ses, caption, siyah kare, sessizlik, tekrar senaryo
- YouTube Data API: yükleme, thumbnail, playlist, schedule (`publishAt`)
- YouTube Analytics API v2: views/likes/AVR (token yoksa atlanır)
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

Tek giriş: `python3 -m automation`. `python3 -m kanallar` aynı fabrikaya yönlendirir (`bilim-dakikasi` → `channel_01`).

## YouTube

1. YouTube Data API v3 + OAuth masaüstü istemcisi
2. `client_secret.json`
3. `python3 -m automation produce --upload` — video **private** gider

Browser ile Studio’ya tıklamak yok. Resmi API yoksa üretim yerel kalır.

## Mimari kararlar

Tek çekirdek: `automation/pipeline.py`. Eski `kanallar/` paketindeki catalog/test yardımcıları durur; üretim ve stüdyo yeni hatta akar. İkinci kanal yok.

Asset sırası: yerel slayt → Commons referans (attribution) → stock/AI yok. Telifli video indirilmez.

## GitHub’da bakılan, bilinçli alınmayan / alınan

| Repo | Karar | Gerekçe |
| --- | --- | --- |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | Akış alındı, repo vendor edilmedi | 100+ araç / ücretli video üretici; bizim MVP $0 + tek hat |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) + [template-tiktok](https://github.com/remotion-dev/template-tiktok) | Şablon bizde; Whisper şablonu yok | 1.5GB model MVP’yi şişirir; ASS altyazı yeterli |
| [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | Alındı | Sadece metadata; kopya yükleme yok |
| Wikimedia Commons API | Alındı | Ücretsiz, lisanslı still referans |
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | Soyutlama | Upload için kullanılmaz |
| [rhasspy/piper](https://github.com/rhasspy/piper) | Sonra | İyi offline TTS; model indirimi ayrı iş |
| Codebase Memory MCP | İsteğe bağlı | `scripts/index_codebase.py` yeterli |

Açılmayanlar: Ruflo, LangGraph, Redis, Kubernetes, swarm, OpenViking.

## Bilinçli olarak sonraya bırakılanlar

OpenViking, browser-use gerçek sürücü, n8n, ücretli AI video, ikinci kanal. Codebase Memory binary: `python3 scripts/index_codebase.py`.

## Test

```bash
pytest -q
```
