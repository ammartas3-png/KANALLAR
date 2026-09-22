-- Canonical PostgreSQL schema. SQLAlchemy create_all also applies this model.

CREATE TABLE IF NOT EXISTS channels (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    youtube_channel_id TEXT DEFAULT '',
    niche TEXT DEFAULT 'science',
    language TEXT DEFAULT 'tr',
    country TEXT DEFAULT 'TR',
    status TEXT DEFAULT 'active',
    content_style TEXT DEFAULT 'cards',
    voice TEXT DEFAULT '',
    daily_video_limit INTEGER DEFAULT 2,
    publish_times TEXT DEFAULT '08:00',
    timezone TEXT DEFAULT 'UTC',
    llm_provider TEXT DEFAULT 'auto',
    tts_provider TEXT DEFAULT 'auto',
    image_provider TEXT DEFAULT 'kie',
    video_provider TEXT DEFAULT 'kie',
    template_id TEXT DEFAULT 'shorts_default',
    enabled BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS ideas (
    id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL REFERENCES channels(id),
    topic TEXT NOT NULL,
    source TEXT DEFAULT 'catalog',
    score DOUBLE PRECISION DEFAULT 0,
    status TEXT DEFAULT 'NEW',
    angle TEXT DEFAULT '',
    hook_candidate TEXT DEFAULT '',
    payload_json TEXT DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scripts (
    id TEXT PRIMARY KEY,
    idea_id TEXT NOT NULL REFERENCES ideas(id),
    hook TEXT DEFAULT '',
    script TEXT DEFAULT '',
    cta TEXT DEFAULT '',
    version INTEGER DEFAULT 1,
    payload_json TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS videos (
    id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL REFERENCES channels(id),
    script_id TEXT NOT NULL REFERENCES scripts(id),
    idea_id TEXT DEFAULT '',
    filepath TEXT DEFAULT '',
    preview_url TEXT DEFAULT '',
    render_url TEXT DEFAULT '',
    duration DOUBLE PRECISION DEFAULT 0,
    status TEXT DEFAULT 'NEW',
    title TEXT DEFAULT '',
    description TEXT DEFAULT '',
    hashtags TEXT DEFAULT '',
    youtube_video_id TEXT DEFAULT '',
    qa_json TEXT DEFAULT '{}',
    cost_per_video DOUBLE PRECISION DEFAULT 0,
    template_id TEXT DEFAULT '',
    prompt_version TEXT DEFAULT '',
    scheduled_at TIMESTAMPTZ,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS video_scenes (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id),
    scene_index INTEGER DEFAULT 0,
    start DOUBLE PRECISION DEFAULT 0,
    duration DOUBLE PRECISION DEFAULT 0,
    narration TEXT DEFAULT '',
    visual_prompt TEXT DEFAULT '',
    motion_prompt TEXT DEFAULT '',
    camera TEXT DEFAULT '',
    text_overlay TEXT DEFAULT '',
    transition TEXT DEFAULT '',
    asset_type TEXT DEFAULT 'image',
    payload_json TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS media_assets (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id),
    scene_id TEXT DEFAULT '',
    kind TEXT DEFAULT 'image',
    provider TEXT DEFAULT '',
    external_job_id TEXT DEFAULT '',
    status TEXT DEFAULT 'queued',
    url TEXT DEFAULT '',
    cost DOUBLE PRECISION DEFAULT 0,
    payload_json TEXT DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS topic_approvals (
    id TEXT PRIMARY KEY,
    idea_id TEXT NOT NULL REFERENCES ideas(id),
    channel_id TEXT DEFAULT '',
    decision TEXT DEFAULT '',
    feedback TEXT DEFAULT '',
    actor TEXT DEFAULT 'telegram',
    token_hash TEXT DEFAULT '',
    consumed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now(),
    decided_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS video_approvals (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id),
    channel_id TEXT DEFAULT '',
    decision TEXT DEFAULT '',
    feedback TEXT DEFAULT '',
    revision_scope TEXT DEFAULT '',
    actor TEXT DEFAULT 'telegram',
    token_hash TEXT DEFAULT '',
    consumed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now(),
    decided_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS uploads (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id),
    youtube_video_id TEXT DEFAULT '',
    title TEXT DEFAULT '',
    description TEXT DEFAULT '',
    publish_time TIMESTAMPTZ,
    status TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id),
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    subscribers_gained INTEGER DEFAULT 0,
    average_view_duration DOUBLE PRECISION DEFAULT 0,
    retention DOUBLE PRECISION DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    ctr DOUBLE PRECISION DEFAULT 0,
    collected_at TIMESTAMPTZ DEFAULT now(),
    time_window TEXT DEFAULT '1h'
);

CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id),
    experiment_id TEXT DEFAULT '',
    hook_type TEXT DEFAULT '',
    video_style TEXT DEFAULT 'cards',
    voice TEXT DEFAULT '',
    duration DOUBLE PRECISION DEFAULT 0,
    title_style TEXT DEFAULT '',
    prompt_version TEXT DEFAULT '',
    template_id TEXT DEFAULT '',
    visual_style TEXT DEFAULT '',
    result TEXT DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS memory (
    id SERIAL PRIMARY KEY,
    channel_id TEXT NOT NULL REFERENCES channels(id),
    type TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 0.5,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS content_patterns (
    id SERIAL PRIMARY KEY,
    channel_id TEXT NOT NULL REFERENCES channels(id),
    pattern_type TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    evidence_json TEXT DEFAULT '{}',
    confidence DOUBLE PRECISION DEFAULT 0.5,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS human_feedback (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    channel_id TEXT DEFAULT '',
    scope TEXT DEFAULT '',
    feedback TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workflow_runs (
    id TEXT PRIMARY KEY,
    workflow TEXT NOT NULL,
    entity_id TEXT DEFAULT '',
    channel_id TEXT DEFAULT '',
    status TEXT DEFAULT 'RUNNING',
    attempt INTEGER DEFAULT 1,
    n8n_execution_id TEXT DEFAULT '',
    error_summary TEXT DEFAULT '',
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS workflow_events (
    id SERIAL PRIMARY KEY,
    run_id TEXT DEFAULT '',
    entity_id TEXT DEFAULT '',
    event_type TEXT NOT NULL,
    message TEXT DEFAULT '',
    payload_json TEXT DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS errors (
    id SERIAL PRIMARY KEY,
    source TEXT DEFAULT '',
    entity_id TEXT DEFAULT '',
    code TEXT DEFAULT '',
    message TEXT DEFAULT '',
    payload_json TEXT DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id SERIAL PRIMARY KEY,
    agent TEXT NOT NULL,
    video_id TEXT DEFAULT '',
    input_json TEXT DEFAULT '{}',
    output_json TEXT DEFAULT '{}',
    duration_ms INTEGER DEFAULT 0,
    token_usage INTEGER DEFAULT 0,
    api_cost DOUBLE PRECISION DEFAULT 0,
    error TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS used_topics (
    id SERIAL PRIMARY KEY,
    channel_id TEXT NOT NULL REFERENCES channels(id),
    topic_key TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS render_jobs (
    id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id),
    status TEXT DEFAULT 'queued',
    preview_url TEXT DEFAULT '',
    final_url TEXT DEFAULT '',
    error TEXT DEFAULT '',
    payload_json TEXT DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
