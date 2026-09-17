from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/kanallar.db"
    kanallar_host: str = "127.0.0.1"
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
    youtube_api_key: str = ""
    pexels_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
