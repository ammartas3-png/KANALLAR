from kanallar.catalog.loader import load_catalog, pick_topic
from kanallar.config import load_channel
from kanallar.script import build_script


def test_catalogs_are_unique_and_complete():
    for name in ("science_tr", "history_tr"):
        topics = load_catalog(name)
        assert len(topics) >= 10
        ids = [topic.id for topic in topics]
        assert len(ids) == len(set(ids))
        for topic in topics:
            assert topic.title
            assert topic.hook
            assert len(topic.facts) >= 2
            assert topic.closer


def test_pick_skips_used_topics():
    first = pick_topic("science_tr")
    second = pick_topic("science_tr", used_ids={first.id})
    assert second.id != first.id


def test_script_has_shorts_metadata():
    channel = load_channel("bilim-dakikasi")
    topic = pick_topic(channel.catalog, topic_id="ahtapot-uc-kalp")
    script = build_script(channel, topic)
    assert script["title"].endswith("#shorts")
    assert len(script["scenes"]) >= 5
    assert script["scenes"][0]["role"] == "hook"
    assert script["scenes"][-1]["role"] == "cta"
    assert "üç kalbi" in script["narration"]
    assert "Sentetik ses" in script["description"]
