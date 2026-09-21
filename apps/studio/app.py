from __future__ import annotations

import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from analytics.queries import dashboard_stats
from automation.bootstrap import bootstrap_cloud_secrets
from automation.jobs import list_awaiting_approval
from automation.pipeline import approve_and_maybe_upload, produce, reject
from channels.loader import load_channel
from config.paths import APPS_DIR, CONTENT_DIR
from config.settings import get_settings
from database.models import Video
from database.session import get_session, init_db
from media.router import status_report
from storage import storage_status
from youtube.api import credentials_status

WEB = APPS_DIR / "studio"
templates = Jinja2Templates(directory=str(WEB / "templates"))
app = FastAPI(title="Kanallar", version="0.4.0")
app.mount("/static", StaticFiles(directory=str(WEB / "static")), name="static")


@app.on_event("startup")
def _startup() -> None:
    bootstrap_cloud_secrets()
    init_db()


@app.get("/health")
def health() -> dict:
    settings = get_settings()
    yt = credentials_status()
    return {
        "ok": True,
        "run_mode": settings.run_mode,
        "youtube": yt,
        "storage": storage_status(),
        "media": status_report(),
        "pending": len(list_awaiting_approval()),
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    channel = load_channel()
    stats = dashboard_stats()
    settings = get_settings()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "channel": channel,
            "stats": stats,
            "youtube": credentials_status(),
            "pending": list_awaiting_approval(),
            "media": status_report(),
            "require_human_approval": settings.require_human_approval,
        },
    )


@app.post("/api/produce")
def api_produce(topic: str | None = None) -> dict:
    def _run() -> None:
        produce(topic_id=topic)

    threading.Thread(target=_run, daemon=True).start()
    return {"status": "started"}


@app.post("/api/approve/{video_id}")
def api_approve(video_id: str, upload: bool = True) -> dict:
    result = approve_and_maybe_upload(video_id, upload=upload)
    if not result.get("ok"):
        raise HTTPException(400, result)
    return result


@app.post("/api/reject/{video_id}")
def api_reject(video_id: str, reason: str = "") -> dict:
    result = reject(video_id, reason=reason)
    if not result.get("ok"):
        raise HTTPException(400, result)
    return result


@app.get("/api/pending")
def api_pending() -> list:
    return list_awaiting_approval()


@app.get("/api/media-status")
def api_media_status() -> dict:
    return status_report()


@app.get("/api/stats")
def api_stats() -> dict:
    return dashboard_stats()


@app.get("/media/{video_id}")
def media(video_id: str) -> FileResponse:
    with get_session() as session:
        row = session.get(Video, video_id)
    path = Path(row.filepath) if row and row.filepath else CONTENT_DIR / "videos" / video_id / "final.mp4"
    if not path.exists():
        raise HTTPException(404, "Video yok")
    return FileResponse(path, media_type="video/mp4")
