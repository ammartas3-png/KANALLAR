FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RUN_MODE=cloud \
    KANALLAR_HOST=0.0.0.0 \
    KANALLAR_PORT=8080 \
    STORAGE_BACKEND=local

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    espeak-ng \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8080
# Always-on cloud entry: Studio API + cron produce/analytics (no Mac)
CMD ["python", "-m", "automation.worker"]
