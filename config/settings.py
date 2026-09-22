from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # cloud = always-on worker assumptions (0.0.0.0 bind, require durable storage when s3)
    run_mode: str = "cloud"  # cloud | local
    database_url: str = "sqlite:///./data/kanallar.db"
    kanallar_host: str = "0.0.0.0"
    kanallar_port: int = 8080
    active_channel: str = "channel_01"
    renderer: str = "ffmpeg"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    ollama_base_url: str = "http://127.0.0.1:11434"
    llm_cheap_model: str = "gpt-4o-mini"
    llm_normal_model: str = "gpt-4o-mini"
    llm_premium_model: str = "gpt-4o-mini"
    voice_provider: str = "auto"
    elevenlabs_api_key: str = ""
    google_tts_api_key: str = ""
    youtube_client_secrets: str = "client_secret.json"
    youtube_token: str = "token.json"
    # Prefer these on cloud hosts (paste JSON or base64) — no Mac file copy
    youtube_client_secrets_json: str = ""
    youtube_token_json: str = ""
    youtube_api_key: str = ""
    pexels_api_key: str = ""
    # Media gateways (optional until keys exist)
    kie_api_key: str = ""
    kie_callback_url: str = ""
    kie_default_image_model: str = ""
    kie_default_video_model: str = ""
    kie_default_voice_model: str = ""
    hf_api_key_id: str = ""
    hf_api_key_secret: str = ""
    hf_default_image_endpoint: str = ""
    hf_default_video_endpoint: str = ""
    hf_default_voice_endpoint: str = ""
    require_human_approval: bool = True
    # HARD publish gate — even after video approval, default blocks auto upload
    auto_publish: bool = False
    dry_run: bool = True
    max_daily_videos: int = 4
    max_generation_retries: int = 2
    max_media_regenerations: int = 2
    topic_similarity_cooldown_days: int = 45
    # Media: hybrid = local cards + Kie only on wow/hook scenes when keyed
    media_quality: str = "hybrid"  # local | hybrid | auto | cheap | premium
    kie_wow_roles_only: bool = True  # hook/cta only when hybrid
    max_kie_scenes_per_video: int = 1
    # Telegram approval (n8n holds bot token; worker may verify shared secret)
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    approval_webhook_secret: str = ""
    # Object storage
    storage_backend: str = "local"  # local | s3
    storage_bucket: str = ""
    storage_access_key: str = ""
    storage_secret_key: str = ""
    storage_endpoint: str = ""  # R2/MinIO endpoint
    storage_region: str = "auto"
    storage_public_base_url: str = ""  # CDN / public R2 URL
    # Worker schedule (UTC)
    worker_produce_cron: str = "0 8 * * *"  # daily 08:00 UTC
    worker_analytics_hourly: bool = True
    worker_enable_studio: bool = True
    # Public base URL of this worker (for n8n + Telegram preview links)
    public_base_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
