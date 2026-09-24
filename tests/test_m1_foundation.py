from database.states import (
    VideoStatus,
    can_publish,
    canonicalize_video_status,
)
from automation.approvals import (
    consume_topic_approval,
    consume_video_approval,
    has_valid_video_publish_approval,
    issue_topic_approval,
    issue_video_approval,
)
from database.models import Channel, Idea, Script, Video
from database.session import get_session, init_db
from automation.jobs import save_checkpoint, load_checkpoint, approve_video


def _seed(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/m1.db")
    monkeypatch.setenv("DRY_RUN", "true")
    monkeypatch.setenv("AUTO_PUBLISH", "false")
    from config.settings import get_settings

    get_settings.cache_clear()
    init_db()
    with get_session() as session:
        session.add(Channel(id="channel_01", name="Test", enabled=True))
        session.add(Idea(id="idea1", channel_id="channel_01", topic="t", status="TOPIC_PENDING_APPROVAL"))
        session.add(Script(id="script1", idea_id="idea1"))
        session.add(
            Video(
                id="vid1",
                channel_id="channel_01",
                script_id="script1",
                filepath="/tmp/x.mp4",
                duration=20,
                status="awaiting_approval",
                qa_json="{}",
            )
        )


def test_canonicalize_legacy_status():
    assert canonicalize_video_status("awaiting_approval") == VideoStatus.VIDEO_PENDING_APPROVAL
    assert can_publish(VideoStatus.VIDEO_APPROVED)
    assert not can_publish(VideoStatus.VIDEO_PENDING_APPROVAL)


def test_topic_approval_token_roundtrip(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    issued = issue_topic_approval("idea1", channel_id="channel_01")
    bad = consume_topic_approval("not-a-token", decision="APPROVE")
    assert bad["ok"] is False
    ok = consume_topic_approval(issued["token"], decision="APPROVE")
    assert ok["ok"] is True
    assert ok["idea_id"] == "idea1"
    # single use
    again = consume_topic_approval(issued["token"], decision="APPROVE")
    assert again["ok"] is False


def test_video_approval_required_for_publish_record(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    assert has_valid_video_publish_approval("vid1") is False
    issued = issue_video_approval("vid1", channel_id="channel_01")
    consume_video_approval(issued["token"], decision="PUBLISH")
    assert has_valid_video_publish_approval("vid1") is True


def test_approve_sets_canonical_status(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    save_checkpoint("vid1", "awaiting_approval")
    ok = approve_video("vid1")
    assert ok["ok"] is True
    assert load_checkpoint("vid1")["status"] == VideoStatus.VIDEO_APPROVED


def test_dry_run_blocks_youtube(tmp_path, monkeypatch):
    _seed(tmp_path, monkeypatch)
    monkeypatch.setenv("DRY_RUN", "true")
    from config.settings import get_settings
    from automation.pipeline import approve_and_maybe_upload

    get_settings.cache_clear()
    save_checkpoint("vid1", "awaiting_approval")
    result = approve_and_maybe_upload("vid1", upload=True, force_legacy=True)
    assert result["ok"] is True
    assert result["upload"]["status"] == "dry_run_skipped"
