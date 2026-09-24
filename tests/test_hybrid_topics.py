from automation.topics import generate_topic_candidates, get_pending_topics
from database.session import init_db
from config.settings import get_settings


def test_research_shortlist_no_media(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/topics.db")
    get_settings.cache_clear()
    init_db()
    # seed channel row not strictly required for catalog load
    result = generate_topic_candidates(channel_id="channel_01", limit=12)
    assert result["status"] == "TOPIC_PENDING_APPROVAL"
    assert result["candidate_count"] >= 1
    assert len(result["shortlist"]) >= 1
    assert result["note"].startswith("Media")
    for c in result["shortlist"]:
        assert "idea_id" in c
        assert "score" in c
        assert "signals" in c
    pending = get_pending_topics("channel_01")
    assert len(pending) >= 1


def test_hybrid_assets_default_local(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/hy.db")
    monkeypatch.setenv("MEDIA_QUALITY", "hybrid")
    monkeypatch.setenv("KIE_API_KEY", "")
    get_settings.cache_clear()
    init_db()
    from agents.asset_agent import plan_assets
    from channels.loader import load_channel

    channel = load_channel()
    script = {
        "topic": "Test",
        "hook": "Hook",
        "scenes": [
            {"role": "hook", "text": "a", "visual": "ocean"},
            {"role": "body", "text": "b", "visual": "lab"},
        ],
    }
    assets = plan_assets(channel, script)
    assert assets["kie_scenes"] == 0
    assert assets["provider"] == "local"
    assert all(s["provider"] == "local" for s in assets["scenes"])
