from __future__ import annotations

import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from kanallar.catalog.loader import load_catalog
from kanallar.config import list_channels, load_channel
from kanallar.paths import WEB_DIR, job_dir
from kanallar.pipeline import publish, queue_job, run_job
from kanallar.store import Store
from kanallar.youtube_upload import credentials_status

templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))
store = Store()
app = FastAPI(title="Kanallar", version="0.1.0")
app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")

STEP_LABELS = {
    "queued": "Sırada",
    "writing": "Senaryo yazılıyor",
    "narrating": "Seslendiriliyor",
    "designing": "Sahne kartları",
    "rendering": "Video kuruluyor",
    "ready": "Yayına hazır",
    "uploading": "YouTube'a gidiyor",
    "uploaded": "Yüklendi",
    "failed": "Hata",
}


def _channel_view(channel_id: str) -> dict:
    channel = load_channel(channel_id)
    catalog = load_catalog(channel.catalog)
    used = store.used_topic_ids(channel.id)
    jobs = store.list_jobs(channel.id)
    return {
        "id": channel.id,
        "name": channel.name,
        "tagline": channel.tagline,
        "niche": channel.niche,
        "format": channel.format,
        "voice": channel.voice,
        "language": channel.language,
        "accent": channel.brand.accent,
        "primary": channel.brand.primary,
        "topics_total": len(catalog),
        "topics_used": len(used),
        "topics_left": max(0, len(catalog) - len(used)),
        "jobs": [job.to_dict() for job in jobs],
        "job_count": len(jobs),
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    channels = [_channel_view(channel.id) for channel in list_channels()]
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "channels": channels,
            "counts": store.counts(),
            "youtube": credentials_status(),
        },
    )


@app.get("/channels/{channel_id}", response_class=HTMLResponse)
def channel_page(request: Request, channel_id: str) -> HTMLResponse:
    try:
        view = _channel_view(channel_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    return templates.TemplateResponse(
        request,
        "channel.html",
        {"channel": view, "youtube": credentials_status(), "steps": STEP_LABELS},
    )


@app.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_page(request: Request, job_id: str) -> HTMLResponse:
    try:
        job = store.get(job_id)
    except KeyError as exc:
        raise HTTPException(404, "İş bulunamadı") from exc
    channel = load_channel(job.channel_id)
    return templates.TemplateResponse(
        request,
        "job.html",
        {
            "job": job.to_dict(),
            "channel": channel,
            "youtube": credentials_status(),
            "steps": STEP_LABELS,
        },
    )


@app.get("/api/channels")
def api_channels() -> list[dict]:
    return [_channel_view(channel.id) for channel in list_channels()]


@app.post("/api/channels/{channel_id}/produce")
def api_produce(channel_id: str, topic_id: str | None = None) -> dict:
    try:
        load_channel(channel_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    job = queue_job(channel_id, store, topic_id)
    thread = threading.Thread(target=run_job, args=(job.id, store), daemon=True)
    thread.start()
    return job.to_dict()


@app.get("/api/jobs/{job_id}")
def api_job(job_id: str) -> dict:
    try:
        return store.get(job_id).to_dict()
    except KeyError as exc:
        raise HTTPException(404, "İş bulunamadı") from exc


@app.post("/api/jobs/{job_id}/upload")
def api_upload(job_id: str) -> dict:
    if not credentials_status()["client_secrets"]:
        raise HTTPException(400, "YouTube OAuth dosyası yok. client_secret.json ekleyin.")
    try:
        return publish(job_id, store)
    except KeyError as exc:
        raise HTTPException(404, "İş bulunamadı") from exc
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/media/jobs/{job_id}/video")
def media_video(job_id: str) -> FileResponse:
    path = Path(store.get(job_id).video_path or job_dir(job_id) / "video.mp4")
    if not path.exists():
        raise HTTPException(404, "Video henüz yok")
    return FileResponse(path, media_type="video/mp4", filename=f"{job_id}.mp4")


@app.get("/media/jobs/{job_id}/thumb")
def media_thumb(job_id: str) -> FileResponse:
    path = Path(store.get(job_id).thumb_path or job_dir(job_id) / "thumbnail.png")
    if not path.exists():
        raise HTTPException(404, "Kapak henüz yok")
    return FileResponse(path, media_type="image/png")
