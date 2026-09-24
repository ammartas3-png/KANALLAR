from kanallar.config import list_channels, load_channel


def test_default_channels_load():
    channels = list_channels()
    ids = {channel.id for channel in channels}
    assert ids == {"bilim-dakikasi", "tarih-kisa"}


def test_bilim_is_shorts():
    channel = load_channel("bilim-dakikasi")
    assert channel.is_shorts
    assert channel.video_size == (1080, 1920)
    assert channel.voice.startswith("tr-TR")
