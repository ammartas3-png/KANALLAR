from channels.loader import load_channel
from kanallar.cli import MVP_ALIASES


def test_single_entry_aliases():
    assert "channel_01" in MVP_ALIASES
    assert "bilim-dakikasi" in MVP_ALIASES
    channel = load_channel("channel_01")
    assert channel.upload.playlist_id == ""
    assert channel.id == "channel_01"


def test_youtube_upload_signature():
    from youtube.api import upload_short

    assert callable(upload_short)
