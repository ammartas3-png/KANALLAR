from __future__ import annotations

from datetime import datetime, timezone

import httplib2
import pytest
from googleapiclient.errors import HttpError

from channels.loader import load_channel
from youtube import api as yt
from youtube.guard import BLOCKED_CHANNEL_IDS, ChannelGuardError, assert_upload_allowed

PERSONAL = "UCa-ulc77JRueoWa11LPQUVg"
MONEY = "UCj6vC105nA-2P627Q01cIgw"


class _Call:
    def __init__(self, result=None, error=None):
        self._result, self._error = result, error

    def execute(self):
        if self._error:
            raise self._error
        return self._result


class _Insert:
    def next_chunk(self):
        return None, {"id": "vid123"}


class FakeYouTube:
    def __init__(self, channel_id: str, thumbnail_error: HttpError | None = None):
        self.channel_id = channel_id
        self.thumbnail_error = thumbnail_error
        self.inserted: list[dict] = []

    def channels(self):
        outer = self

        class _Channels:
            def list(self, **_):
                return _Call({"items": [{"id": outer.channel_id}] if outer.channel_id else []})

        return _Channels()

    def videos(self):
        outer = self

        class _Videos:
            def insert(self, part, body, media_body):
                outer.inserted.append(body)
                return _Insert()

        return _Videos()

    def thumbnails(self):
        outer = self

        class _Thumbs:
            def set(self, **_):
                return _Call({}, outer.thumbnail_error)

        return _Thumbs()


@pytest.fixture()
def money():
    return load_channel("money_in_a_minute")


@pytest.fixture()
def fake_media(monkeypatch):
    import googleapiclient.http

    monkeypatch.setattr(googleapiclient.http, "MediaFileUpload", lambda *a, **k: object())


def _script() -> dict:
    return {"title": "Rule of 72", "description": "Doubling money", "tags": ["money"]}


def test_personal_channel_is_blocked():
    assert PERSONAL in BLOCKED_CHANNEL_IDS
    with pytest.raises(ChannelGuardError):
        assert_upload_allowed(PERSONAL, PERSONAL)
    with pytest.raises(ChannelGuardError):
        assert_upload_allowed(MONEY, PERSONAL)


@pytest.mark.parametrize(
    ("expected", "authorised"),
    [("", MONEY), (MONEY, ""), (MONEY, "UCsomethingElse")],
)
def test_guard_rejects_missing_or_mismatched_ids(expected, authorised):
    with pytest.raises(ChannelGuardError):
        assert_upload_allowed(expected, authorised)


def test_guard_allows_matching_brand_channel():
    assert_upload_allowed(MONEY, MONEY)


def test_upload_refuses_personal_token_before_sending_video(tmp_path, monkeypatch, money, fake_media):
    fake = FakeYouTube(PERSONAL)
    monkeypatch.setattr(yt, "_client", lambda key: fake)
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    with pytest.raises(ChannelGuardError):
        yt.upload_short(money, _script(), video, None)
    assert fake.inserted == []


def test_upload_disabled_when_channel_id_missing(tmp_path, monkeypatch, fake_media):
    history = load_channel("history_in_a_minute")
    history.youtube_channel_id = ""
    monkeypatch.setattr(yt, "_client", lambda key: pytest.fail("must not build a client"))
    with pytest.raises(ChannelGuardError):
        yt.upload_short(history, _script(), tmp_path / "v.mp4", None)


def test_thumbnail_403_keeps_uploaded_video_id(tmp_path, monkeypatch, money, fake_media):
    error = HttpError(httplib2.Response({"status": 403}), b'{"error":{"message":"needs verification"}}')
    fake = FakeYouTube(MONEY, thumbnail_error=error)
    monkeypatch.setattr(yt, "_client", lambda key: fake)
    video, thumb = tmp_path / "v.mp4", tmp_path / "t.png"
    video.write_bytes(b"x")
    thumb.write_bytes(b"x")
    result = yt.upload_short(money, _script(), video, thumb)
    assert result["youtube_id"] == "vid123"
    assert result["thumbnail_error"].startswith("403")
    status = fake.inserted[0]["status"]
    assert status["containsSyntheticMedia"] is True
    assert status["selfDeclaredMadeForKids"] is False


def test_upload_agent_reports_blocked_channel(tmp_path, monkeypatch, money):
    from agents.upload_agent import agent as upload_agent

    monkeypatch.setattr(upload_agent, "credentials_status", lambda key: {"client_secrets": True, "token": True})

    def _blocked(*_a, **_k):
        raise ChannelGuardError("token engelli kanala ait")

    monkeypatch.setattr(upload_agent, "upload_short", _blocked)
    out = upload_agent.publish.__wrapped__(money, _script(), tmp_path / "v.mp4", None)
    assert out["status"] == "blocked_channel"


def test_publish_at_uses_schedule_hour(money):
    money.upload.schedule_publish = True
    now = datetime(2026, 9, 24, 15, 0, tzinfo=timezone.utc)
    assert yt.next_publish_at(money, now) == "2026-09-25T14:00:00Z"
    money.upload.schedule_publish = False
    assert yt.next_publish_at(money, now) is None
    body = yt.build_upload_body(money, _script(), "2026-09-25T14:00:00Z")
    assert body["status"]["privacyStatus"] == "private"
    assert body["status"]["publishAt"] == "2026-09-25T14:00:00Z"
    assert "personal finance" in body["snippet"]["tags"]


def test_tokens_are_per_channel(tmp_path, monkeypatch):
    from config.settings import get_settings

    monkeypatch.setenv("YOUTUBE_TOKENS_DIR", str(tmp_path))
    get_settings.cache_clear()
    assert yt.token_path("money_in_a_minute") == tmp_path / "money_in_a_minute.json"
    with pytest.raises(yt.YouTubeConfigError):
        yt.token_path("")
    get_settings.cache_clear()


def test_brand_channel_configs_follow_channels_status():
    money = load_channel("money_in_a_minute")
    science = load_channel("science_in_a_minute")
    history = load_channel("history_in_a_minute")
    assert money.youtube_channel_id == MONEY
    assert science.youtube_channel_id == "UCjmDhWo0I7KIPKVTDBZZbqg"
    assert history.youtube_channel_id == "UCDn9Qz6jZ_ikwm37yuD4NOg"
    assert (money.upload.category_id, science.upload.category_id, history.upload.category_id) == ("27", "28", "27")
    for channel in (money, science, history):
        assert channel.language == "en" and channel.upload.default_language == "en"
        assert channel.upload.privacy == "private" and channel.upload.made_for_kids is False
        assert channel.youtube_channel_id not in BLOCKED_CHANNEL_IDS
        assert channel.catalog_path().exists()


def test_director_scores_against_channel_median():
    from agents.director_agent.agent import score_groups

    scored = score_groups({"question": [300, 500], "fact": [50, 70], "solo": [900]}, channel_median=200)
    assert scored["question"]["verdict"] == "win"
    assert scored["fact"]["verdict"] == "lose"
    assert scored["solo"]["verdict"] == "insufficient"


def test_qa_flags_unlicensed_assets():
    from agents.qa_agent.agent import unlicensed_assets

    assets = {
        "scenes": [{"provider": "local"}, {"provider": "kie"}, {"provider": "stockgrab"}],
        "commons_refs": [{"title": "Map", "license": "CC BY-SA 4.0", "used": True}, {"title": "Photo", "license": "", "used": True}],
    }
    problems = unlicensed_assets(assets)
    assert problems == ["scene3:provider=stockgrab", "ref:Photo:no-license"]


def test_qa_fails_when_captions_not_burned(tmp_path, monkeypatch):
    from agents.qa_agent import agent as qa

    meta = {
        "is_1080x1920": True, "is_9_16": True, "duration": 30, "has_audio": True, "has_video": True,
        "size_bytes": 500_000, "black_segments": [], "silence_segments": [],
    }
    monkeypatch.setattr(qa, "validate_short", lambda path: dict(meta))
    monkeypatch.setattr(qa, "_duplicate_narration", lambda *a, **k: False)
    video, captions = tmp_path / "v.mp4", tmp_path / "c.ass"
    video.write_bytes(b"x")
    captions.write_text("x" * 100)
    script = {"hook": "h", "scenes": [{"text": "t"}], "narration": "n"}
    burned = qa.inspect.__wrapped__(video, captions, script, captions_burned=True, assets={"scenes": [{"provider": "local"}]})
    fallback = qa.inspect.__wrapped__(video, captions, script, captions_burned=False, assets={"scenes": [{"provider": "local"}]})
    assert burned["ok"] is True
    assert fallback["ok"] is False and fallback["checks"]["captions_burned"] is False
