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
from channels.loader import ChannelConfig, load_channel
from config.paths import CONTENT_DIR, ensure_runtime_dirs
from database.models import Channel, Experiment, Idea, Script, Upload, Video
from database.session import get_session, init_db
from memory.store import mark_used
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


def produce(channel_id: str | None = None, topic_id: str | None = None, upload: bool = False) -> dict:
    init_db()
    ensure_runtime_dirs()
    channel = load_channel(channel_id)
    seed_channel(channel)
    video_id = _id()
    work = CONTENT_DIR / "videos" / video_id
    work.mkdir(parents=True, exist_ok=True)

    brief = research(channel, topic_id=topic_id, video_id=video_id, log_input={"topic_id": topic_id})
    idea = ideate(channel, brief, video_id=video_id, log_input={"topic": brief["topic"]})
    script = write_script(channel, idea, video_id=video_id, log_input={"topic": idea["topic"]})
    assets = plan_assets(channel, script, video_id=video_id, log_input={"engine": "local"})
    if assets.get("commons_refs"):
        lines = ["", "Görsel referans (Wikimedia Commons, gömülmedi):"]
        for ref in assets["commons_refs"][:3]:
            lines.append(f"- {ref.get('title')} {ref.get('page')} ({ref.get('license')})")
        script["description"] = script["description"].rstrip() + "\n" + "\n".join(lines)
    voice = narrate(channel, script, work, video_id=video_id, log_input={"chars": len(script["narration"])})
    rendered = compose_short(channel, script, Path(voice["audio"]), work)
    qa = inspect(rendered["video"], rendered["captions"], script, video_id=video_id, log_input={"file": str(rendered["video"])})

    idea_id, script_id = _id(), _id()
    with get_session() as session:
        session.add(
            Idea(
                id=idea_id,
                channel_id=channel.id,
                topic=idea["topic"],
                source="catalog",
                score=float(idea.get("novelty_score") or 0),
                status="used",
                payload_json=json.dumps(idea, ensure_ascii=False),
            )
        )
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
        session.add(
            Video(
                id=video_id,
                channel_id=channel.id,
                script_id=script_id,
                filepath=str(rendered["video"]),
                duration=float(rendered["duration"]),
                status="qa_passed" if qa["ok"] else "qa_failed",
                qa_json=json.dumps(qa, ensure_ascii=False),
            )
        )
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
    (work / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")

    upload_result = {"status": "not_requested"}
    if not qa["ok"]:
        upload_result = {"status": "blocked_qa"}
    elif upload:
        upload_result = publish(
            channel,
            script,
            rendered["video"],
            rendered["thumb"],
            video_id=video_id,
            log_input={"privacy": channel.upload.privacy},
        )
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
            if row is not None:
                row.status = "uploaded" if upload_result.get("status") == "uploaded" else row.status

    learn(channel.id, video_id=video_id, log_input={"after": video_id})
    cost = video_cost(video_id)
    with get_session() as session:
        row = session.get(Video, video_id)
        if row is not None:
            row.cost_per_video = cost

    public = CONTENT_DIR / "public" / f"{video_id}.mp4"
    public.parent.mkdir(parents=True, exist_ok=True)
    if rendered["video"].exists():
        shutil.copy2(rendered["video"], public)

    return {
        "id": video_id,
        "channel_id": channel.id,
        "topic": idea["topic"],
        "title": script["title"],
        "status": "ready" if qa["ok"] else "qa_failed",
        "qa": qa,
        "voice_engine": voice.get("engine"),
        "duration": rendered["duration"],
        "filepath": str(rendered["video"]),
        "thumb": str(rendered["thumb"]),
        "cost_per_video": cost,
        "upload": upload_result,
        "assets": assets["engine"],
    }


def refresh_analytics(window: str = "24h") -> dict:
    init_db()
    return collect_analytics(window=window, log_input={"window": window})
