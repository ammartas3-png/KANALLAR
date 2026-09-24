from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from kanallar.config import ChannelConfig
from kanallar.slides import FONT_BOLD, FONT_MEDIUM, _font, _hex, wrap_text


def render_thumbnail(channel: ChannelConfig, title: str, hook: str, output: Path) -> Path:
    width, height = 1280, 720
    primary = _hex(channel.brand.primary)
    accent = _hex(channel.brand.accent)
    ink = _hex(channel.brand.text)

    image = Image.new("RGBA", (width, height), (*primary, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, 28, height), fill=(*accent, 255))
    draw.ellipse((width - 520, -180, width + 80, 420), fill=(*accent, 40))
    draw.polygon(
        [(width, height), (width - 380, height), (width, height - 260)],
        fill=(*accent, 50),
    )

    kicker_font = _font(FONT_MEDIUM, 28)
    title_font = _font(FONT_BOLD, 72)
    hook_font = _font(FONT_BOLD, 36)

    draw.text((72, 56), channel.name.upper(), font=kicker_font, fill=accent)
    lines = wrap_text(draw, title, title_font, width - 160)
    y = 150
    for line in lines[:3]:
        draw.text((72, y), line, font=title_font, fill=ink)
        y += 84
    hook_lines = wrap_text(draw, hook, hook_font, width - 200)
    y += 16
    for line in hook_lines[:2]:
        draw.text((72, y), line, font=hook_font, fill=(*ink, 210))
        y += 48

    image = image.filter(ImageFilter.SMOOTH).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "PNG")
    return output
