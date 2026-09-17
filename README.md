# Kanallar

Otomasyonlu YouTube stüdyosu. Kanal profilinden konuyu seçer, orijinal senaryo yazar, sentetik ses üretir, sahne kartlarını ve kapağı çizer, Shorts MP4’ünü kurar. YouTube yüklemesi resmi Data API ile ve varsayılan olarak **gizli**dir.

Hazır kanallar:

| Kanal | Biçim | Dil | Katalog |
| --- | --- | --- | --- |
| **Bilim Dakikası** | Shorts 9:16 | Türkçe | 18 bilimsel konu |
| **Tarih Kısa** | Shorts 9:16 | Türkçe | 12 tarih sahnesi |

## Hızlı başlangıç

```bash
python3 -m pip install -r requirements.txt
python3 -m kanallar channels
python3 -m kanallar produce bilim-dakikasi
python3 -m kanallar studio --host 127.0.0.1 --port 8080
```

Stüdyo arayüzü `http://127.0.0.1:8080` adresinde açılır. `Video üret` kuyruğa iş koyar; bitince videoyu oynatır ve MP4 indirir.

Belirli bir konu:

```bash
python3 -m kanallar produce bilim-dakikasi --topic ahtapot-uc-kalp
python3 -m kanallar produce tarih-kisa --topic gobeklitepe
```

## Yeni kanal

`channels/yeni-kanal.yaml` ekleyin. `catalog` alanı `kanallar/catalog/` altındaki bir YAML dosyasına işaret eder. Her konu `id`, `title`, `hook`, `facts`, `closer`, `tags` ister.

Cron ile günlük üretim:

```bash
0 9 * * * cd /path/to/KANALLAR && python3 -m kanallar produce bilim-dakikasi
```

## YouTube yükleme

1. [Google Cloud Console](https://console.cloud.google.com/) içinde YouTube Data API v3’ü açın.
2. OAuth masaüstü istemcisi oluşturun, JSON’u `client_secret.json` olarak koyun.
3. İlk yüklemede tarayıcıda hesabı onaylayın. Token `token.json` içine yazılır.
4. Stüdyodan veya CLI’dan yükleyin:

```bash
python3 -m kanallar upload <job_id>
```

Videolar `private` gider. Toplu spam yükleme için tasarlanmadı.

## Ne üretilir, ne üretilmez

- Senaryolar katalogdaki orijinal metinlerden kurulur; başka kanallardan kopyalanmaz.
- Görseller Pillow ile çizilir, ses `edge-tts` (yoksa `espeak-ng`) ile üretilir.
- Telifli müzik katılmaz.
- Açıklamada sentetik ses / otomatik kurgu belirtilir.

## Test

```bash
pytest -q
```
