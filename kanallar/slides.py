from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from kanallar.config import ChannelConfig

FONT_REGULAR = Path("/usr/share/fonts/truetype/macos/Inter-Regular.ttf")
FONT_MEDIUM = Path("/usr/share/fonts/truetype/macos/Inter-Medium.ttf")
FONT_BOLD = Path("/usr/share/fonts/truetype/macos/Inter-Bold.ttf")
FONT_FALLBACK = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    candidate = path if path.exists() else FONT_FALLBACK
    if not candidate.exists():
        return ImageFont.load_default()
    return ImageFont.truetype(str(candidate), size=size)


def _hex(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def render_slide(
    channel: ChannelConfig,
    text: str,
    role: str,
    index: int,
    total: int,
    output: Path,
    topic_title: str,
) -> Path:
    width, height = channel.video_size
    primary = _hex(channel.brand.primary)
    accent = _hex(channel.brand.accent)
    ink = _hex(channel.brand.text)
    muted = _hex(channel.brand.muted)

    band = Image.new("RGB", (1, height), primary)
    band_px = band.load()
    for y in range(height):
        mix = 1 - abs((y / max(height - 1, 1)) - 0.35)
        band_px[0, y] = tuple(
            min(255, int(primary[i] + (accent[i] - primary[i]) * 0.16 * mix)) for i in range(3)
        )
    image = band.resize((width, height), Image.Resampling.BILINEAR).convert("RGBA")

    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((width - 720, -240, width + 180, 660), fill=(*accent, 28))
    draw.ellipse((-280, height - 760, 520, height + 80), fill=(*accent, 18))
    draw.rectangle((0, 0, 18, height), fill=(*accent, 255))

    kicker_font = _font(FONT_MEDIUM, 36)
    title_font = _font(FONT_BOLD, 52)
    body_font = _font(FONT_BOLD, 64 if role in {"hook", "closer"} else 56)
    meta_font = _font(FONT_REGULAR, 30)

    kicker = channel.name.upper()
    draw.text((80, 96), kicker, font=kicker_font, fill=accent)
    draw.text((80, 156), topic_title, font=title_font, fill=muted)

    role_label = {
        "hook": "AÇILIŞ",
        "fact": f"GERÇEK {index}",
        "closer": "KAPANIS",
        "cta": "ABONE OL",
    }.get(role, role.upper())
    draw.text((80, 240), role_label, font=meta_font, fill=accent)

    max_width = width - 160
    lines = wrap_text(draw, text, body_font, max_width)
    line_height = 84 if role in {"hook", "closer"} else 76
    block_height = len(lines) * line_height
    y = max(360, (height - block_height) // 2 - 40)
    for line in lines:
        draw.text((80, y), line, font=body_font, fill=ink)
        y += line_height

    bar_y = height - 140
    draw.rounded_rectangle((80, bar_y, width - 80, bar_y + 10), radius=6, fill=(*muted, 70))
    progress = max(0.08, index / max(total, 1))
    draw.rounded_rectangle(
        (80, bar_y, 80 + int((width - 160) * progress), bar_y + 10),
        radius=6,
        fill=accent,
    )
    draw.text((80, bar_y + 28), channel.tagline, font=meta_font, fill=muted)

    image = image.filter(ImageFilter.SMOOTH).convert("RGB")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, "PNG")
    return output
