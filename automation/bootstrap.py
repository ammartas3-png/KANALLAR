from __future__ import annotations

import base64
import json
import logging
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


def bootstrap_cloud_secrets() -> dict:
    """Materialize OAuth JSON files from env so Mac/local disk is never required."""
    ensure_runtime_dirs()
    settings = get_settings()
    secrets_path = Path(settings.youtube_client_secrets)
    if not secrets_path.is_absolute():
        secrets_path = ROOT / secrets_path
    token_path = Path(settings.youtube_token)
    if not token_path.is_absolute():
        token_path = ROOT / token_path

    wrote_secrets = _write_json_secret(
        secrets_path,
        settings.youtube_client_secrets_json,
        "YOUTUBE_CLIENT_SECRETS_JSON",
    )
    wrote_token = _write_json_secret(
        token_path,
        settings.youtube_token_json,
        "YOUTUBE_TOKEN_JSON",
    )
    return {
        "client_secrets_from_env": wrote_secrets or secrets_path.exists(),
        "token_from_env": wrote_token or token_path.exists(),
        "client_secrets_path": str(secrets_path),
        "token_path": str(token_path),
        "run_mode": settings.run_mode,
    }
