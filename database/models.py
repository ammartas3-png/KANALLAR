from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    youtube_channel_id: Mapped[str] = mapped_column(String(64), default="")
    niche: Mapped[str] = mapped_column(String(64), default="science")
    language: Mapped[str] = mapped_column(String(8), default="tr")
    country: Mapped[str] = mapped_column(String(8), default="TR")
    status: Mapped[str] = mapped_column(String(32), default="active")
    content_style: Mapped[str] = mapped_column(String(64), default="cards")
    voice: Mapped[str] = mapped_column(String(64), default="")
    daily_video_limit: Mapped[int] = mapped_column(Integer, default=2)
    publish_times: Mapped[str] = mapped_column(String(200), default="08:00")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    llm_provider: Mapped[str] = mapped_column(String(64), default="auto")
    tts_provider: Mapped[str] = mapped_column(String(64), default="auto")
    image_provider: Mapped[str] = mapped_column(String(64), default="kie")
    video_provider: Mapped[str] = mapped_column(String(64), default="kie")
    template_id: Mapped[str] = mapped_column(String(64), default="shorts_default")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"))
    topic: Mapped[str] = mapped_column(String(300))
    source: Mapped[str] = mapped_column(String(64), default="catalog")
    score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(32), default="NEW")
    angle: Mapped[str] = mapped_column(String(300), default="")
    hook_candidate: Mapped[str] = mapped_column(Text, default="")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Script(Base):
    __tablename__ = "scripts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey("ideas.id"))
    hook: Mapped[str] = mapped_column(Text, default="")
    script: Mapped[str] = mapped_column(Text, default="")
    cta: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[int] = mapped_column(Integer, default=1)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"))
    script_id: Mapped[str] = mapped_column(ForeignKey("scripts.id"))
    idea_id: Mapped[str] = mapped_column(String(64), default="")
    filepath: Mapped[str] = mapped_column(Text, default="")
    preview_url: Mapped[str] = mapped_column(Text, default="")
    render_url: Mapped[str] = mapped_column(Text, default="")
    duration: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(32), default="NEW")
    title: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    hashtags: Mapped[str] = mapped_column(Text, default="")
    youtube_video_id: Mapped[str] = mapped_column(String(64), default="")
    qa_json: Mapped[str] = mapped_column(Text, default="{}")
    cost_per_video: Mapped[float] = mapped_column(Float, default=0)
    template_id: Mapped[str] = mapped_column(String(64), default="")
    prompt_version: Mapped[str] = mapped_column(String(64), default="")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class VideoScene(Base):
    __tablename__ = "video_scenes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    scene_index: Mapped[int] = mapped_column(Integer, default=0)
    start: Mapped[float] = mapped_column(Float, default=0)
    duration: Mapped[float] = mapped_column(Float, default=0)
    narration: Mapped[str] = mapped_column(Text, default="")
    visual_prompt: Mapped[str] = mapped_column(Text, default="")
    motion_prompt: Mapped[str] = mapped_column(Text, default="")
    camera: Mapped[str] = mapped_column(String(64), default="")
    text_overlay: Mapped[str] = mapped_column(Text, default="")
    transition: Mapped[str] = mapped_column(String(64), default="")
    asset_type: Mapped[str] = mapped_column(String(32), default="image")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    scene_id: Mapped[str] = mapped_column(String(64), default="")
    kind: Mapped[str] = mapped_column(String(32), default="image")
    provider: Mapped[str] = mapped_column(String(64), default="")
    external_job_id: Mapped[str] = mapped_column(String(128), default="")
    status: Mapped[str] = mapped_column(String(32), default="queued")
    url: Mapped[str] = mapped_column(Text, default="")
    cost: Mapped[float] = mapped_column(Float, default=0)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TopicApproval(Base):
    __tablename__ = "topic_approvals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    idea_id: Mapped[str] = mapped_column(ForeignKey("ideas.id"))
    channel_id: Mapped[str] = mapped_column(String(64), default="")
    decision: Mapped[str] = mapped_column(String(32), default="")
    feedback: Mapped[str] = mapped_column(Text, default="")
    actor: Mapped[str] = mapped_column(String(64), default="telegram")
    token_hash: Mapped[str] = mapped_column(String(128), default="")
    consumed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class VideoApproval(Base):
    __tablename__ = "video_approvals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    channel_id: Mapped[str] = mapped_column(String(64), default="")
    decision: Mapped[str] = mapped_column(String(32), default="")
    feedback: Mapped[str] = mapped_column(Text, default="")
    revision_scope: Mapped[str] = mapped_column(String(64), default="")  # TITLE|SCRIPT|VOICE|SCENE|FULL_VIDEO
    actor: Mapped[str] = mapped_column(String(64), default="telegram")
    token_hash: Mapped[str] = mapped_column(String(128), default="")
    consumed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    youtube_video_id: Mapped[str] = mapped_column(String(64), default="")
    title: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    publish_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    subscribers_gained: Mapped[int] = mapped_column(Integer, default=0)
    average_view_duration: Mapped[float] = mapped_column(Float, default=0)
    retention: Mapped[float] = mapped_column(Float, default=0)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    ctr: Mapped[float] = mapped_column(Float, default=0)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    time_window: Mapped[str] = mapped_column(String(16), default="1h")


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    experiment_id: Mapped[str] = mapped_column(String(64), default="")
    hook_type: Mapped[str] = mapped_column(String(64), default="")
    video_style: Mapped[str] = mapped_column(String(64), default="cards")
    voice: Mapped[str] = mapped_column(String(64), default="")
    duration: Mapped[float] = mapped_column(Float, default=0)
    title_style: Mapped[str] = mapped_column(String(64), default="")
    prompt_version: Mapped[str] = mapped_column(String(64), default="")
    template_id: Mapped[str] = mapped_column(String(64), default="")
    visual_style: Mapped[str] = mapped_column(String(64), default="")
    result: Mapped[str] = mapped_column(String(32), default="pending")


class MemoryItem(Base):
    __tablename__ = "memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"))
    type: Mapped[str] = mapped_column(String(64))
    key: Mapped[str] = mapped_column(String(200))
    value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ContentPattern(Base):
    __tablename__ = "content_patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"))
    pattern_type: Mapped[str] = mapped_column(String(64))  # winning_hooks | bad_patterns | ...
    key: Mapped[str] = mapped_column(String(200))
    value: Mapped[str] = mapped_column(Text)
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class HumanFeedback(Base):
    __tablename__ = "human_feedback"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(32))  # idea | video
    entity_id: Mapped[str] = mapped_column(String(64))
    channel_id: Mapped[str] = mapped_column(String(64), default="")
    scope: Mapped[str] = mapped_column(String(64), default="")
    feedback: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workflow: Mapped[str] = mapped_column(String(128))
    entity_id: Mapped[str] = mapped_column(String(64), default="")
    channel_id: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="RUNNING")
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    n8n_execution_id: Mapped[str] = mapped_column(String(64), default="")
    error_summary: Mapped[str] = mapped_column(Text, default="")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WorkflowEvent(Base):
    __tablename__ = "workflow_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), default="")
    entity_id: Mapped[str] = mapped_column(String(64), default="")
    event_type: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(Text, default="")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ErrorLog(Base):
    __tablename__ = "errors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), default="")
    entity_id: Mapped[str] = mapped_column(String(64), default="")
    code: Mapped[str] = mapped_column(String(64), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent: Mapped[str] = mapped_column(String(64))
    video_id: Mapped[str] = mapped_column(String(64), default="")
    input_json: Mapped[str] = mapped_column(Text, default="{}")
    output_json: Mapped[str] = mapped_column(Text, default="{}")
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    token_usage: Mapped[int] = mapped_column(Integer, default=0)
    api_cost: Mapped[float] = mapped_column(Float, default=0)
    error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class UsedTopic(Base):
    __tablename__ = "used_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id"))
    topic_key: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class RenderJob(Base):
    __tablename__ = "render_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    video_id: Mapped[str] = mapped_column(ForeignKey("videos.id"))
    status: Mapped[str] = mapped_column(String(32), default="queued")
    preview_url: Mapped[str] = mapped_column(Text, default="")
    final_url: Mapped[str] = mapped_column(Text, default="")
    error: Mapped[str] = mapped_column(Text, default="")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
