from __future__ import annotations

import json
from pathlib import Path

from kanallar.catalog.loader import pick_topic
from kanallar.config import ChannelConfig, load_channel
from kanallar.paths import job_dir
from kanallar.script import build_script
from kanallar.slides import render_slide
from kanallar.store import Job, Store
from kanallar.thumbnail import render_thumbnail
from kanallar.tts import synthesize
from kanallar.video import audio_duration, render_video, scene_durations
from kanallar.youtube_upload import upload_video
import uuid


def new_job_id() -> str:
    return uuid.uuid4().hex[:12]


def queue_job(channel_id: str, store: Store | None = None, topic_id: str | None = None) -> Job:
    store = store or Store()
    channel = load_channel(channel_id)
    topic = pick_topic(channel.catalog, used_ids=store.used_topic_ids(channel_id), topic_id=topic_id)
    script = build_script(channel, topic)
    return store.create_job(new_job_id(), channel.id, topic.id, script["title"])


def produce(
    channel_id: str,
    store: Store | None = None,
    topic_id: str | None = None,
    upload: bool = False,
) -> dict:
    store = store or Store()
    job = queue_job(channel_id, store, topic_id)
    return run_job(job.id, store, upload)


def run_job(job_id: str, store: Store | None = None, upload: bool = False) -> dict:
    store = store or Store()
    job = store.get(job_id)
    channel = load_channel(job.channel_id)
    topic = pick_topic(channel.catalog, topic_id=job.topic_id)
    script = build_script(channel, topic)
    work = job_dir(job_id)
    try:
        return _run_steps(channel, script, job_id, work, store, upload)
    except Exception as exc:
        store.update(job_id, status="failed", step="failed", error=str(exc))
        raise


def _run_steps(
    channel: ChannelConfig,
    script: dict,
    job_id: str,
    work: Path,
    store: Store,
    upload: bool,
) -> dict:
    store.update(
        job_id,
        status="running",
        step="writing",
        title=script["title"],
        script_json=json.dumps(script, ensure_ascii=False),
    )
    (work / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")

    store.update(job_id, step="narrating")
    audio_path = work / "narration.mp3"
    script["voice_engine"] = synthesize(script["narration"], audio_path, channel)
    (work / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    store.update(job_id, script_json=json.dumps(script, ensure_ascii=False))

    store.update(job_id, step="designing", audio_path=str(audio_path))
    slides: list[Path] = []
    scenes = script["scenes"]
    for index, scene in enumerate(scenes, start=1):
        slide = work / "slides" / f"{index:02d}.png"
        render_slide(
            channel,
            scene["text"],
            scene["role"],
            index,
            len(scenes),
            slide,
            script["topic_title"],
        )
        slides.append(slide)

    thumb_path = work / "thumbnail.png"
    render_thumbnail(channel, script["topic_title"], script["hook"], thumb_path)

    store.update(job_id, step="rendering", thumb_path=str(thumb_path))
    duration = audio_duration(audio_path)
    durations = scene_durations([scene["text"] for scene in scenes], duration)
    video_path = work / "video.mp4"
    render_video(slides, durations, audio_path, video_path, channel.video_size)

    store.update(job_id, status="ready", step="ready", video_path=str(video_path), error="")
    if upload:
        return publish(job_id, store)
    return store.get(job_id).to_dict()


def publish(job_id: str, store: Store | None = None) -> dict:
    store = store or Store()
    job = store.get(job_id)
    if not job.video_path:
        raise RuntimeError("Önce videoyu üretin.")
    channel = load_channel(job.channel_id)
    store.update(job_id, step="uploading", status="uploading")
    try:
        result = upload_video(
            channel,
            job.script(),
            Path(job.video_path),
            Path(job.thumb_path) if job.thumb_path else None,
        )
    except Exception as exc:
        store.update(job_id, status="ready", step="ready", error=str(exc))
        raise
    store.update(
        job_id,
        status="uploaded",
        step="uploaded",
        youtube_id=result["youtube_id"],
        youtube_url=result["youtube_url"],
        error="",
    )
    return store.get(job_id).to_dict()
