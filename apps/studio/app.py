from __future__ import annotations

import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from analytics.queries import dashboard_stats
from automation.pipeline import produce
from channels.loader import load_channel
from config.paths import APPS_DIR, CONTENT_DIR
from database.models import Video
from database.session import get_session, init_db
from youtube.api import credentials_status

WEB = APPS_DIR / "studio"
templates = Jinja2Templates(directory=str(WEB / "templates"))
app = FastAPI(title="Kanallar", version="0.2.0")
app.mount("/static", StaticFiles(directory=str(WEB / "static")), name="static")


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    channel = load_channel()
    stats = dashboard_stats()
    return templates.TemplateResponse(
        request,
        "index.html",
        {"channel": channel, "stats": stats, "youtube": credentials_status()},
    )


@app.post("/api/produce")
def api_produce(topic: str | None = None) -> dict:
    def _run() -> None:
        produce(topic_id=topic)

    threading.Thread(target=_run, daemon=True).start()
    return {"status": "started"}


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
