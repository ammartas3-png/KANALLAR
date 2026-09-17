-- Canonical PostgreSQL schema. SQLAlchemy create_all also applies this model.

CREATE TABLE IF NOT EXISTS channels (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    youtube_channel_id TEXT DEFAULT '',
    niche TEXT DEFAULT 'science',
    language TEXT DEFAULT 'tr',
    country TEXT DEFAULT 'TR',
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS ideas (
    id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL REFERENCES channels(id),
    topic TEXT NOT NULL,
    source TEXT DEFAULT 'catalog',
    score DOUBLE PRECISION DEFAULT 0,
    status TEXT DEFAULT 'new',
    payload_json TEXT DEFAULT '{}'
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
    filepath TEXT DEFAULT '',
    duration DOUBLE PRECISION DEFAULT 0,
    status TEXT DEFAULT 'queued',
    qa_json TEXT DEFAULT '{}',
    cost_per_video DOUBLE PRECISION DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
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
    window TEXT DEFAULT '1h'
);

CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(id),
    hook_type TEXT DEFAULT '',
    video_style TEXT DEFAULT 'cards',
    voice TEXT DEFAULT '',
    duration DOUBLE PRECISION DEFAULT 0,
    title_style TEXT DEFAULT '',
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
