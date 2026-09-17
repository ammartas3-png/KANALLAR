from agents.idea_agent import ideate
from agents.script_agent import write_script
from agents.asset_agent import plan_assets
from agents.qa_agent import inspect
from channels.loader import load_channel
from database.models import Channel
from database.session import get_session, init_db
from video.captions import build_ass, chunk_words, word_timings


def test_single_mvp_channel():
    channel = load_channel()
    assert channel.id == "channel_01"
    assert channel.catalog_path().exists()


def test_script_json_shape(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/t.db")
    from config.settings import get_settings

    get_settings.cache_clear()
    init_db()
    channel = load_channel()
    brief = {
        "catalog_item": {
            "id": "ahtapot-uc-kalp",
            "title": "Ahtapotun Üç Kalbi",
            "hook": "Ahtapotun üç kalbi var.",
            "facts": ["Kanı mavidir.", "Kolları düşünür."],
            "closer": "Zeka yayılmıştır.",
            "tags": ["ahtapot"],
            "visual": "ocean",
        },
        "topic": "Ahtapotun Üç Kalbi",
        "reason": "test",
        "estimated_potential": 0.7,
        "source_urls": [],
    }
    idea = ideate(channel, brief)
    script = write_script(channel, idea)
    assets = plan_assets(channel, script)
    assert script["scenes"][0]["role"] == "hook"
    assert script["scenes"][-1]["role"] == "cta"
    assert script["estimated_duration"] >= 18
    assert assets["engine"] == "local_cards"


def test_captions_word_chunks(tmp_path):
    timings = word_timings("bir iki üç dört beş altı", 6)
    assert len(timings) == 6
    chunks = chunk_words(timings, 4)
    assert len(chunks[0]) == 4
    ass = build_ass("bir iki üç dört beş", 5, tmp_path / "c.ass")
    text = ass.read_text(encoding="utf-8")
    assert "Dialogue:" in text
    assert "Kanallar" in text


def test_qa_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/q.db")
    from config.settings import get_settings

    get_settings.cache_clear()
    init_db()
    result = inspect(tmp_path / "missing.mp4", None, {"hook": "x", "scenes": [1]})
    assert result["ok"] is False


def test_db_seed(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/db.db")
    from config.settings import get_settings

    get_settings.cache_clear()
    init_db()
    with get_session() as session:
        session.add(Channel(id="channel_01", name="Bilim Dakikası"))
    with get_session() as session:
        assert session.get(Channel, "channel_01") is not None
