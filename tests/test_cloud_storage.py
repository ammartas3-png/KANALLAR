import json
from pathlib import Path

from storage.local import LocalStorage
from storage import get_storage, storage_status, sync_video_artifacts


def test_local_storage_put(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.setenv("RUN_MODE", "cloud")
    from config.settings import get_settings

    get_settings.cache_clear()
    store = LocalStorage(root=tmp_path / "obj")
    src = tmp_path / "a.mp4"
    src.write_bytes(b"fake")
    url = store.put_file("videos/x/final.mp4", str(src), "video/mp4")
    assert Path(url).exists()
    assert (tmp_path / "obj" / "videos" / "x" / "final.mp4").exists()


def test_storage_status_keys(monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    from config.settings import get_settings

    get_settings.cache_clear()
    report = storage_status()
    assert "local" in report
    assert "s3" in report
    assert report["backend"] == "local"


def test_sync_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.setenv("RUN_MODE", "cloud")
    from config.settings import get_settings

    get_settings.cache_clear()
    monkeypatch.setattr("storage.local.CONTENT_DIR", tmp_path / "content")
    video = tmp_path / "final.mp4"
    thumb = tmp_path / "t.png"
    video.write_bytes(b"v")
    thumb.write_bytes(b"t")
    meta = sync_video_artifacts("vid99", video, thumb)
    assert meta["backend"] == "local"
    assert "video" in meta["urls"]


def test_bootstrap_writes_token(tmp_path, monkeypatch):
    secrets = {"installed": {"client_id": "x", "client_secret": "y"}}
    token = {"token": "abc", "refresh_token": "r", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "x", "client_secret": "y"}
    monkeypatch.setenv("YOUTUBE_CLIENT_SECRETS", str(tmp_path / "cs.json"))
    monkeypatch.setenv("YOUTUBE_TOKEN", str(tmp_path / "tok.json"))
    monkeypatch.setenv("YOUTUBE_CLIENT_SECRETS_JSON", json.dumps(secrets))
    monkeypatch.setenv("YOUTUBE_TOKEN_JSON", json.dumps(token))
    from config.settings import get_settings
    from automation.bootstrap import bootstrap_cloud_secrets

    get_settings.cache_clear()
    result = bootstrap_cloud_secrets()
    assert result["client_secrets_from_env"] is True
    assert result["token_from_env"] is True
    assert (tmp_path / "cs.json").exists()
    assert (tmp_path / "tok.json").exists()


def test_health_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/h.db")
    monkeypatch.setenv("RUN_MODE", "cloud")
    from config.settings import get_settings
    from starlette.testclient import TestClient
    from apps.studio.app import app

    get_settings.cache_clear()
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "storage" in body
