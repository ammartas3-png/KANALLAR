from automation.jobs import (
    RESUME_LOCKED_STATUSES,
    approve_video,
    load_checkpoint,
    reject_video,
    save_checkpoint,
)
from database.models import Channel, Idea, Script, Video
from database.session import get_session, init_db


def _seed(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/jobs.db")
    from config.settings import get_settings

    get_settings.cache_clear()
    init_db()
    with get_session() as session:
        session.add(Channel(id="channel_01", name="Test"))
        session.add(Idea(id="idea1", channel_id="channel_01", topic="t"))
        session.add(Script(id="script1", idea_id="idea1"))
        session.add(
            Video(
                id="vid1",
                channel_id="channel_01",
                script_id="script1",
                filepath="/tmp/x.mp4",
                duration=20,
                status="queued",
                qa_json="{}",
            )
        )


def test_checkpoint_roundtrip(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    save_checkpoint("vid1", "research", brief_topic="x")
    save_checkpoint("vid1", "qa", qa_result={"ok": True})
    cp = load_checkpoint("vid1")
    assert cp["stage"] == "qa"
    assert "research" in cp["completed_stages"]
    assert "qa" in cp["completed_stages"]


def test_approval_flow(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    save_checkpoint("vid1", "awaiting_approval", qa_result={"ok": True})
    ok = approve_video("vid1")
    assert ok["ok"] is True
    assert load_checkpoint("vid1")["status"] == "VIDEO_APPROVED"


def test_reject_flow(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    save_checkpoint("vid1", "awaiting_approval")
    result = reject_video("vid1", reason="hook zayıf")
    assert result["ok"] is True
    cp = load_checkpoint("vid1")
    assert cp["status"] == "VIDEO_REJECTED"
    assert cp["qa"]["reject_reason"] == "hook zayıf"


def test_asset_plan_includes_provider(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/a.db")
    monkeypatch.setenv("MEDIA_QUALITY", "local")
    from agents.asset_agent import plan_assets
    from channels.loader import load_channel
    from config.settings import get_settings

    get_settings.cache_clear()
    init_db()
    channel = load_channel()
    script = {
        "topic": "Test",
        "hook": "Hook",
        "scenes": [{"role": "hook", "text": "a", "visual": "ocean"}],
    }
    assets = plan_assets(channel, script)
    assert assets["provider"] == "local"
    assert assets["engine"] == "local_cards"
    assert assets["scenes"][0]["provider"] == "local"


def test_resume_locked_on_terminal_status(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    monkeypatch.setenv("REQUIRE_HUMAN_APPROVAL", "true")
    from config.settings import get_settings
    from automation.pipeline import produce

    get_settings.cache_clear()
    save_checkpoint(
        "vid1",
        "uploaded",
        completed_stages=["research", "idea", "script", "assets", "voice", "render", "qa", "uploaded"],
        qa_result={"ok": True},
    )
    assert "uploaded" in RESUME_LOCKED_STATUSES
    result = produce(resume_id="vid1")
    assert result["error"] == "resume_locked"
    assert result["status"] == "uploaded"
    assert load_checkpoint("vid1")["status"] == "uploaded"


def test_resume_locked_awaiting_approval(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    from config.settings import get_settings
    from automation.pipeline import produce

    get_settings.cache_clear()
    save_checkpoint(
        "vid1",
        "awaiting_approval",
        completed_stages=["research", "idea", "script", "assets", "voice", "render", "qa"],
        qa_result={"ok": True},
    )
    result = produce(resume_id="vid1", upload=True, force_upload=True)
    assert result["error"] == "resume_locked"
    assert result["status"] == "awaiting_approval"
    assert load_checkpoint("vid1")["status"] == "awaiting_approval"
