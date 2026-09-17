from kanallar.store import Store


def test_job_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setenv("KANALLAR_DATA", str(tmp_path))
    store = Store(tmp_path / "test.db")
    job = store.create_job("abc123", "bilim-dakikasi", "ahtapot-uc-kalp", "Deneme")
    assert job.status == "queued"
    store.update("abc123", status="ready", video_path=str(tmp_path / "v.mp4"))
    loaded = store.get("abc123")
    assert loaded.status == "ready"
    assert store.used_topic_ids("bilim-dakikasi") == {"ahtapot-uc-kalp"}
    assert store.counts()["ready"] == 1
