from __future__ import annotations

import base64
import json
import logging
import os
from pathlib import Path

from config.paths import ROOT, ensure_runtime_dirs
from config.settings import get_settings

log = logging.getLogger("kanallar.bootstrap")


def _write_json_secret(path: Path, raw: str, label: str) -> bool:
    text = (raw or "").strip()
    if not text:
        return False
    # Allow base64-wrapped JSON for easier secret managers
    if not text.startswith("{"):
        try:
            text = base64.b64decode(text).decode("utf-8")
        except Exception:  # noqa: BLE001
            log.warning("%s decode failed", label)
            return False
    try:
        json.loads(text)
    except json.JSONDecodeError:
        log.warning("%s is not valid JSON", label)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    log.info("Wrote %s from env", path.name)
    return True


TOKEN_ENV_PREFIX = "YOUTUBE_TOKEN_JSON__"


def channel_token_envs(environ: dict[str, str]) -> dict[str, str]:
    """Map YOUTUBE_TOKEN_JSON__<CHANNEL_KEY> env vars to channel keys (lowercase)."""
    return {
        name[len(TOKEN_ENV_PREFIX):].lower(): value
        for name, value in environ.items()
        if name.startswith(TOKEN_ENV_PREFIX) and value.strip()
    }


def bootstrap_cloud_secrets() -> dict:
    """Materialize OAuth JSON files from env so Mac/local disk is never required."""
    from youtube.api import token_path, tokens_dir

    ensure_runtime_dirs()
    settings = get_settings()
    secrets_path = Path(settings.youtube_client_secrets)
    if not secrets_path.is_absolute():
        secrets_path = ROOT / secrets_path

    wrote_secrets = _write_json_secret(
        secrets_path,
        settings.youtube_client_secrets_json,
        "YOUTUBE_CLIENT_SECRETS_JSON",
    )
    if os.environ.get("YOUTUBE_TOKEN_JSON", "").strip():
        log.warning("YOUTUBE_TOKEN_JSON is ignored: it belongs to the blocked personal channel")
    tokens = {
        key: _write_json_secret(token_path(key), raw, f"{TOKEN_ENV_PREFIX}{key.upper()}")
        for key, raw in channel_token_envs(dict(os.environ)).items()
    }
    return {
        "client_secrets_from_env": wrote_secrets or secrets_path.exists(),
        "channel_tokens": sorted(k for k, ok in tokens.items() if ok),
        "client_secrets_path": str(secrets_path),
        "tokens_dir": str(tokens_dir()),
        "run_mode": settings.run_mode,
    }
