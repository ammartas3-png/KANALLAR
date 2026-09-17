from pathlib import Path

from kanallar.config import load_channel
from kanallar.slides import render_slide, wrap_text
from kanallar.thumbnail import render_thumbnail
from kanallar.video import scene_durations
from PIL import Image, ImageDraw, ImageFont


def test_wrap_keeps_words():
    image = Image.new("RGB", (800, 200))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    lines = wrap_text(draw, "kısa kısa kısa kelimeler burada durur", font, 80)
    assert len(lines) > 1
    assert all(lines)


def test_slide_and_thumb_render(tmp_path):
    channel = load_channel("bilim-dakikasi")
    slide = render_slide(
        channel,
        "Ahtapotun üç kalbi var.",
        "hook",
        1,
        5,
        tmp_path / "slide.png",
        "Ahtapotun Üç Kalbi",
    )
    thumb = render_thumbnail(channel, "Ahtapotun Üç Kalbi", "Üç kalp, mavi kan.", tmp_path / "thumb.png")
    assert Image.open(slide).size == (1080, 1920)
    assert Image.open(thumb).size == (1280, 720)


def test_scene_durations_cover_audio():
    durations = scene_durations(["a" * 20, "b" * 40, "c" * 20], 12)
    assert len(durations) == 3
    assert all(item >= 1.2 for item in durations)
    assert abs(sum(durations) - 12) < 0.05


def test_paths_exist():
    assert Path("channels/bilim-dakikasi.yaml").exists()
    assert Path("kanallar/catalog/science_tr.yaml").exists()
