from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

from agents.analytics_agent import collect as collect_analytics
from agents.asset_agent import plan_assets
from agents.director_agent import learn
from agents.idea_agent import ideate
from agents.qa_agent import inspect
from agents.research_agent import research
from agents.script_agent import write_script
from agents.upload_agent import publish
from agents.voice_agent import narrate
from analytics.cost import video_cost
from automation.jobs import (
    RESUME_LOCKED_STATUSES,
    approve_video,
    load_checkpoint,
    mark_failed,
    reject_video,
    save_checkpoint,
)
from channels.loader import ChannelConfig, load_channel
from config.paths import CONTENT_DIR, ensure_runtime_dirs
from config.settings import get_settings
from database.models import Channel, Experiment, Idea, Script, Upload, Video
from database.session import get_session, init_db
from database.states import VideoStatus
from media.router import status_report
from memory.store import mark_used
from storage import sync_video_artifacts
from video.compose import compose_short


def _id() -> str:
    return uuid.uuid4().hex[:12]


def seed_channel(channel: ChannelConfig) -> None:
    with get_session() as session:
        if session.get(Channel, channel.id) is None:
            session.add(
                Channel(
                    id=channel.id,
                    name=channel.name,
                    youtube_channel_id=channel.youtube_channel_id,
                    niche=channel.niche,
                    language=channel.language,
                    country=channel.country,
                    status="active",
                )
            )


def _persist_shell(video_id: str, channel_id: str, idea: dict, script: dict, idea_id: str, script_id: str) -> None:
    with get_session() as session:
        idea_row = session.get(Idea, idea_id)
        if idea_row is None:
            session.add(
                Idea(
                    id=idea_id,
                    channel_id=channel_id,
                    topic=idea["topic"],
                    source="catalog",
                    score=float(idea.get("novelty_score") or 0),
                    status="used",
                    payload_json=json.dumps(idea, ensure_ascii=False),
                )
            )
        else:
            idea_row.topic = idea["topic"]
            idea_row.score = float(idea.get("novelty_score") or 0)
            idea_row.status = "used"
            idea_row.payload_json = json.dumps(idea, ensure_ascii=False)

        script_row = session.get(Script, script_id)
        if script_row is None:
            session.add(
                Script(
                    id=script_id,
                    idea_id=idea_id,
                    hook=script["hook"],
                    script=script["narration"],
                    cta=script["cta"],
                    version=1,
                    payload_json=json.dumps(script, ensure_ascii=False),
                )
            )
        else:
            script_row.hook = script["hook"]
            script_row.script = script["narration"]
            script_row.cta = script["cta"]
            script_row.payload_json = json.dumps(script, ensure_ascii=False)

        video_row = session.get(Video, video_id)
        if video_row is None:
            session.add(
                Video(
                    id=video_id,
                    channel_id=channel_id,
                    script_id=script_id,
                    filepath="",
                    duration=0,
                    status="queued",
                    qa_json="{}",
                )
            )
        else:
            video_row.script_id = script_id
            video_row.channel_id = channel_id


def _record_upload(video_id: str, script: dict, upload_result: dict) -> None:
    with get_session() as session:
        session.add(
            Upload(
                id=_id(),
                video_id=video_id,
                youtube_video_id=upload_result.get("youtube_id") or "",
                title=script["title"],
                description=script["description"],
                status=upload_result.get("status") or "pending",
            )
        )
        row = session.get(Video, video_id)
        if row is not None and upload_result.get("status") == "uploaded":
            row.status = "uploaded"


def produce(
    channel_id: str | None = None,
    topic_id: str | None = None,
    upload: bool = False,
    force_upload: bool = False,
    resume_id: str | None = None,
) -> dict:
    init_db()
    ensure_runtime_dirs()
    settings = get_settings()
    channel = load_channel(channel_id)
    seed_channel(channel)

    video_id = resume_id or _id()
    work = CONTENT_DIR / "videos" / video_id
    work.mkdir(parents=True, exist_ok=True)
    checkpoint = load_checkpoint(video_id) if resume_id else {}
    if resume_id and checkpoint.get("status") in RESUME_LOCKED_STATUSES:
        return {
            "id": video_id,
            "channel_id": checkpoint.get("channel_id") or channel.id,
            "status": checkpoint["status"],
            "filepath": checkpoint.get("filepath") or "",
            "resumed": False,
            "error": "resume_locked",
            "hint": (
                "Bu video terminal durumda; --resume durumu değiştirmez. "
                "Onay için: python -m automation approve --id "
                f"{video_id} --upload"
                if checkpoint["status"]
                in {
                    "awaiting_approval",
                    "approved",
                    VideoStatus.VIDEO_PENDING_APPROVAL,
                    VideoStatus.VIDEO_APPROVED,
                }
                else "Yeni üretim için resume kullanmayın."
            ),
            "qa": checkpoint.get("qa") or {},
            "require_human_approval": settings.require_human_approval,
            "media_providers": status_report(),
        }
    completed = set(checkpoint.get("completed_stages") or [])
    idea_id = checkpoint.get("qa", {}).get("idea_id") or _id()
    script_id = checkpoint.get("script_id") or checkpoint.get("qa", {}).get("script_id") or _id()

    # Create Video row early so stage checkpoints persist from research onward.
    with get_session() as session:
        if session.get(Video, video_id) is None:
            # Placeholder idea/script rows (updated after script stage).
            if session.get(Idea, idea_id) is None:
                session.add(
                    Idea(
                        id=idea_id,
                        channel_id=channel.id,
                        topic="pending",
                        source="catalog",
                        status="draft",
                        payload_json="{}",
                    )
                )
            if session.get(Script, script_id) is None:
                session.add(
                    Script(
                        id=script_id,
                        idea_id=idea_id,
                        payload_json="{}",
                    )
                )
            session.add(
                Video(
                    id=video_id,
                    channel_id=channel.id,
                    script_id=script_id,
                    filepath="",
                    duration=0,
                    status="queued",
                    qa_json=json.dumps({"idea_id": idea_id, "script_id": script_id}, ensure_ascii=False),
                )
            )

    try:
        if "research" not in completed:
            brief = research(channel, topic_id=topic_id, video_id=video_id, log_input={"topic_id": topic_id})
            (work / "brief.json").write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")
            save_checkpoint(video_id, "research", brief_topic=brief.get("topic"), idea_id=idea_id, script_id=script_id)
        else:
            brief = json.loads((work / "brief.json").read_text(encoding="utf-8"))

        if "idea" not in completed:
            idea = ideate(channel, brief, video_id=video_id, log_input={"topic": brief["topic"]})
            (work / "idea.json").write_text(json.dumps(idea, ensure_ascii=False, indent=2), encoding="utf-8")
            save_checkpoint(video_id, "idea", topic=idea.get("topic"), idea_id=idea_id, script_id=script_id)
        else:
            idea = json.loads((work / "idea.json").read_text(encoding="utf-8"))

        if "script" not in completed:
            script = write_script(channel, idea, video_id=video_id, log_input={"topic": idea["topic"]})
            (work / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
            save_checkpoint(video_id, "script", title=script.get("title"), idea_id=idea_id, script_id=script_id)
        else:
            script = json.loads((work / "script.json").read_text(encoding="utf-8"))

        _persist_shell(video_id, channel.id, idea, script, idea_id, script_id)

        if "assets" not in completed:
            assets = plan_assets(
                channel,
                script,
                video_id=video_id,
                quality=settings.media_quality,
                log_input={"engine": settings.media_quality},
            )
            if assets.get("commons_refs"):
                lines = ["", "Görsel referans (Wikimedia Commons, gömülmedi):"]
                for ref in assets["commons_refs"][:3]:
                    lines.append(f"- {ref.get('title')} {ref.get('page')} ({ref.get('license')})")
                script["description"] = script["description"].rstrip() + "\n" + "\n".join(lines)
                (work / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
            (work / "assets.json").write_text(json.dumps(assets, ensure_ascii=False, indent=2), encoding="utf-8")
            save_checkpoint(video_id, "assets", media_provider=assets.get("provider"))
        else:
            assets = json.loads((work / "assets.json").read_text(encoding="utf-8"))

        if "voice" not in completed:
            voice = narrate(channel, script, work, video_id=video_id, log_input={"chars": len(script["narration"])})
            (work / "voice.json").write_text(json.dumps(voice, ensure_ascii=False, indent=2), encoding="utf-8")
            save_checkpoint(video_id, "voice", voice_engine=voice.get("engine"))
        else:
            voice = json.loads((work / "voice.json").read_text(encoding="utf-8"))

        if "render" not in completed:
            rendered = compose_short(channel, script, Path(voice["audio"]), work)
            (work / "render.json").write_text(
                json.dumps(
                    {
                        "video": str(rendered["video"]),
                        "thumb": str(rendered["thumb"]),
                        "captions": str(rendered["captions"]) if rendered.get("captions") else "",
                        "duration": rendered["duration"],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            save_checkpoint(
                video_id,
                "render",
                filepath=str(rendered["video"]),
                duration=rendered["duration"],
            )
        else:
            render_meta = json.loads((work / "render.json").read_text(encoding="utf-8"))
            rendered = {
                "video": Path(render_meta["video"]),
                "thumb": Path(render_meta["thumb"]) if render_meta.get("thumb") else None,
                "captions": Path(render_meta["captions"]) if render_meta.get("captions") else None,
                "duration": render_meta["duration"],
            }

        if "qa" not in completed:
            qa = inspect(
                rendered["video"],
                rendered.get("captions"),
                script,
                video_id=video_id,
                script_id=script_id,
                log_input={"file": str(rendered["video"])},
            )
            save_checkpoint(video_id, "qa", qa_result=qa)
        else:
            qa = load_checkpoint(video_id).get("qa", {}).get("qa_result") or {"ok": True}

        with get_session() as session:
            if session.query(Experiment).filter(Experiment.video_id == video_id).count() == 0:
                session.add(
                    Experiment(
                        video_id=video_id,
                        hook_type=script.get("hook_type") or "fact",
                        video_style=assets.get("engine") or "cards",
                        voice=voice.get("engine") or "",
                        duration=float(rendered["duration"]),
                        title_style="topic_hook",
                        result="pending",
                    )
                )

        mark_used(channel.id, idea["topic_id"])

        upload_result = {"status": "not_requested"}
        final_status = "ready"

        if not qa.get("ok"):
            save_checkpoint(video_id, "failed", failed_stage="qa", qa_result=qa)
            upload_result = {"status": "blocked_qa"}
            final_status = "qa_failed"
        elif settings.require_human_approval and not force_upload:
            save_checkpoint(
                video_id,
                VideoStatus.VIDEO_PENDING_APPROVAL,
                qa_result=qa,
                filepath=str(rendered["video"]),
            )
            upload_result = {
                "status": "awaiting_approval",
                "hint": "Onay için: python -m automation approve --id " + video_id + " --upload",
            }
            final_status = VideoStatus.VIDEO_PENDING_APPROVAL
            if upload:
                upload_result["note"] = (
                    "REQUIRE_HUMAN_APPROVAL=true; --upload yok sayıldı. "
                    "Önce onaylayın veya --force-upload kullanın."
                )
        elif upload or force_upload:
            save_checkpoint(video_id, "uploading")
            upload_result = publish(
                channel,
                script,
                rendered["video"],
                rendered.get("thumb"),
                video_id=video_id,
                log_input={"privacy": channel.upload.privacy},
            )
            _record_upload(video_id, script, upload_result)
            if upload_result.get("status") == "uploaded":
                save_checkpoint(video_id, "uploaded", youtube_id=upload_result.get("youtube_id"))
                final_status = "uploaded"
            else:
                final_status = upload_result.get("status") or "upload_pending"
        else:
            save_checkpoint(video_id, "qa", qa_result=qa, filepath=str(rendered["video"]))
            final_status = "ready"

    except Exception as exc:  # noqa: BLE001 — job boundary
        mark_failed(video_id, stage="produce", error=str(exc))
        raise

    learn(channel.id, video_id=video_id, log_input={"after": video_id})
    cost = video_cost(video_id)
    with get_session() as session:
        row = session.get(Video, video_id)
        if row is not None:
            row.cost_per_video = cost

    public = CONTENT_DIR / "public" / f"{video_id}.mp4"
    public.parent.mkdir(parents=True, exist_ok=True)
    video_path = Path(rendered["video"])
    if video_path.exists():
        shutil.copy2(video_path, public)

    storage_meta = {"backend": "skipped", "urls": {}}
    try:
        storage_meta = sync_video_artifacts(
            video_id,
            video_path,
            Path(rendered["thumb"]) if rendered.get("thumb") else None,
        )
        current = load_checkpoint(video_id).get("status") or final_status
        save_checkpoint(video_id, current, storage=storage_meta)
    except Exception as exc:  # noqa: BLE001 — storage must not kill a good render
        storage_meta = {"backend": "error", "error": str(exc), "urls": {}}

    return {
        "id": video_id,
        "channel_id": channel.id,
        "topic": idea["topic"],
        "title": script["title"],
        "status": final_status,
        "qa": qa,
        "voice_engine": voice.get("engine"),
        "duration": rendered["duration"],
        "filepath": str(rendered["video"]),
        "thumb": str(rendered["thumb"]) if rendered.get("thumb") else "",
        "cost_per_video": cost,
        "upload": upload_result,
        "assets": assets.get("engine"),
        "media_provider": assets.get("provider"),
        "media_providers": status_report(),
        "require_human_approval": settings.require_human_approval,
        "storage": storage_meta,
        "preview_url": (storage_meta.get("urls") or {}).get("video") or "",
    }


def approve_and_maybe_upload(
    video_id: str,
    upload: bool = True,
    *,
    approval_token: str | None = None,
    force_legacy: bool = False,
) -> dict:
    """Mark video approved; optionally publish to YouTube.

    Absolute publish rule:
    - AUTO_PUBLISH must be true OR caller explicitly requests upload
    - DRY_RUN blocks real YouTube calls
    - Prefer a consumed video_approvals row (Telegram token); Studio may use force_legacy
    - Idempotent: existing youtube_video_id skips re-upload
    """
    from automation.approvals import consume_video_approval, has_valid_video_publish_approval
    from database.models import Video as VideoRow
    from database.states import ApprovalDecision, VideoStatus, can_publish

    init_db()
    settings = get_settings()

    if approval_token:
        consumed = consume_video_approval(
            approval_token,
            decision=ApprovalDecision.PUBLISH,
        )
        if not consumed.get("ok"):
            return consumed

    result = approve_video(video_id)
    if not result.get("ok"):
        return result

    if not upload:
        return result

    # Human approval record required unless Studio legacy path creates one now.
    if force_legacy and not has_valid_video_publish_approval(video_id):
        from automation.approvals import issue_video_approval

        issued = issue_video_approval(
            video_id,
            channel_id=load_checkpoint(video_id).get("channel_id") or "",
            actor="studio",
        )
        consume_video_approval(issued["token"], decision=ApprovalDecision.PUBLISH)

    if not has_valid_video_publish_approval(video_id):
        return {
            **result,
            "upload": {
                "status": "blocked_no_approval_record",
                "hint": "Telegram token or Studio approve required",
            },
        }

    # AUTO_PUBLISH=false still allows explicit human-triggered upload after approval.
    if settings.dry_run:
        save_checkpoint(video_id, VideoStatus.VIDEO_APPROVED, dry_run_upload_skipped=True)
        return {
            **result,
            "upload": {"status": "dry_run_skipped", "dry_run": True, "auto_publish": settings.auto_publish},
        }

    with get_session() as session:
        row = session.get(VideoRow, video_id)
        if row and row.youtube_video_id:
            return {
                **result,
                "upload": {
                    "status": "already_uploaded",
                    "youtube_id": row.youtube_video_id,
                    "idempotent": True,
                },
            }

    checkpoint = load_checkpoint(video_id)
    if not can_publish(checkpoint.get("status") or ""):
        return {**result, "upload": {"status": "blocked_status", "status": checkpoint.get("status")}}

    channel = load_channel(checkpoint.get("channel_id"))
    work = CONTENT_DIR / "videos" / video_id
    script = json.loads((work / "script.json").read_text(encoding="utf-8"))
    render_meta = json.loads((work / "render.json").read_text(encoding="utf-8"))
    video = Path(render_meta["video"])
    thumb = Path(render_meta["thumb"]) if render_meta.get("thumb") else None
    save_checkpoint(video_id, VideoStatus.PUBLISHING)
    upload_result = publish(channel, script, video, thumb, video_id=video_id, log_input={"approved": True})
    _record_upload(video_id, script, upload_result)
    if upload_result.get("status") == "uploaded":
        yt_id = upload_result.get("youtube_id") or ""
        save_checkpoint(video_id, VideoStatus.PUBLISHED, youtube_id=yt_id)
        with get_session() as session:
            row = session.get(VideoRow, video_id)
            if row is not None:
                row.youtube_video_id = yt_id
                row.status = VideoStatus.PUBLISHED
    return {**result, "upload": upload_result}


def reject(video_id: str, reason: str = "") -> dict:
    init_db()
    return reject_video(video_id, reason=reason)


def refresh_analytics(window: str = "24h") -> dict:
    init_db()
    return collect_analytics(window=window, log_input={"window": window})
