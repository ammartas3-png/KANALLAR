from kanallar.config import load_channel
from kanallar.tts import synthesize


def test_synthesize_writes_audio(tmp_path):
    channel = load_channel("bilim-dakikasi")
    output = tmp_path / "line.mp3"
    engine = synthesize("Ahtapotun üç kalbi var.", output, channel)
    assert engine in {"edge-tts", "gtts", "espeak-ng"}
    assert output.exists()
    assert output.stat().st_size > 400
