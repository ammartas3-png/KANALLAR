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
        "auto_publish": settings.auto_publish,
        "dry_run": settings.dry_run,
        "require_human_approval": settings.require_human_approval,
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
    # Studio UI = explicit human action → force_legacy creates approval row.
    result = approve_and_maybe_upload(video_id, upload=upload, force_legacy=True)
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


@app.get("/api/video/{video_id}")
def api_video(video_id: str) -> dict:
    with get_session() as session:
        row = session.get(Video, video_id)
    if row is None:
        raise HTTPException(404, "video_not_found")
    return {
        "id": row.id,
        "channel_id": row.channel_id,
        "status": row.status,
        "duration": row.duration,
        "filepath": row.filepath,
        "preview_url": row.preview_url,
        "youtube_video_id": row.youtube_video_id,
        "title": row.title,
    }


@app.post("/api/approvals/topic")
def api_issue_topic_approval(idea_id: str, channel_id: str = "") -> dict:
    from automation.approvals import issue_topic_approval

    return issue_topic_approval(idea_id, channel_id=channel_id, actor="telegram")


@app.post("/api/approvals/topic/decide")
def api_decide_topic(token: str, decision: str, feedback: str = "") -> dict:
    from automation.approvals import consume_topic_approval
    from database.models import Idea
    from database.states import ApprovalDecision, IdeaStatus

    result = consume_topic_approval(token, decision=decision, feedback=feedback)
    if not result.get("ok"):
        raise HTTPException(400, result)
    with get_session() as session:
        idea = session.get(Idea, result["idea_id"])
        if idea is not None:
            if result["decision"] in {ApprovalDecision.APPROVE}:
                idea.status = IdeaStatus.TOPIC_APPROVED
            elif result["decision"] == ApprovalDecision.REJECT:
                idea.status = IdeaStatus.TOPIC_REJECTED
            elif result["decision"] in {ApprovalDecision.REVISE, ApprovalDecision.NEW_IDEAS}:
                idea.status = IdeaStatus.TOPIC_REVISION_REQUESTED
    return result


@app.post("/api/approvals/video")
def api_issue_video_approval(video_id: str, channel_id: str = "") -> dict:
    from automation.approvals import issue_video_approval

    return issue_video_approval(video_id, channel_id=channel_id, actor="telegram")


@app.post("/api/approvals/video/decide")
def api_decide_video(
    token: str,
    decision: str,
    feedback: str = "",
    revision_scope: str = "",
    upload: bool = False,
) -> dict:
    from automation.approvals import consume_video_approval
    from database.states import ApprovalDecision, VideoStatus
    from automation.jobs import save_checkpoint

    result = consume_video_approval(
        token, decision=decision, feedback=feedback, revision_scope=revision_scope
    )
    if not result.get("ok"):
        raise HTTPException(400, result)
    video_id = result["video_id"]
    if result["decision"] in {ApprovalDecision.PUBLISH, ApprovalDecision.APPROVE}:
        save_checkpoint(video_id, VideoStatus.VIDEO_APPROVED, approved=True)
        if upload:
            return approve_and_maybe_upload(video_id, upload=True, force_legacy=False)
    elif result["decision"] == ApprovalDecision.REJECT:
        save_checkpoint(video_id, VideoStatus.VIDEO_REJECTED, approved=False, reject_reason=feedback)
    elif result["decision"] == ApprovalDecision.REVISE:
        save_checkpoint(
            video_id,
            VideoStatus.VIDEO_REVISION_REQUESTED,
            revision_scope=revision_scope,
            feedback=feedback,
        )
    return result


@app.post("/api/workflow-runs")
def api_workflow_run_start(
    workflow: str,
    entity_id: str = "",
    channel_id: str = "",
    n8n_execution_id: str = "",
) -> dict:
    import uuid

    from database.models import WorkflowRun
    from database.states import WorkflowRunStatus

    run_id = uuid.uuid4().hex[:12]
    with get_session() as session:
        session.add(
            WorkflowRun(
                id=run_id,
                workflow=workflow,
                entity_id=entity_id,
                channel_id=channel_id,
                status=WorkflowRunStatus.RUNNING,
                n8n_execution_id=n8n_execution_id,
            )
        )
    return {"id": run_id, "status": WorkflowRunStatus.RUNNING}


@app.patch("/api/workflow-runs/{run_id}")
def api_workflow_run_update(run_id: str, status: str, error_summary: str = "") -> dict:
    from database.models import WorkflowRun, utcnow

    with get_session() as session:
        row = session.get(WorkflowRun, run_id)
        if row is None:
            raise HTTPException(404, "run_not_found")
        row.status = status
        row.error_summary = error_summary
        if status in {"COMPLETED", "FAILED"}:
            row.completed_at = utcnow()
        return {"id": run_id, "status": row.status}


@app.get("/media/{video_id}")
def media(video_id: str) -> FileResponse:
    with get_session() as session:
        row = session.get(Video, video_id)
    path = Path(row.filepath) if row and row.filepath else CONTENT_DIR / "videos" / video_id / "final.mp4"
    if not path.exists():
        raise HTTPException(404, "Video yok")
    return FileResponse(path, media_type="video/mp4")
