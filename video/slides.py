from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from channels.loader import ChannelConfig

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


def render_slide(channel: ChannelConfig, text: str, role: str, index: int, total: int, output: Path, topic_title: str) -> Path:
    width, height = channel.video_size
    primary, accent, ink, muted = map(_hex, (channel.brand.primary, channel.brand.accent, channel.brand.text, channel.brand.muted))
    band = Image.new("RGB", (1, height), primary)
    pixels = band.load()
    for y in range(height):
        mix = 1 - abs((y / max(height - 1, 1)) - 0.35)
        pixels[0, y] = tuple(min(255, int(primary[i] + (accent[i] - primary[i]) * 0.16 * mix)) for i in range(3))
    image = band.resize((width, height), Image.Resampling.BILINEAR).convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((width - 720, -240, width + 180, 660), fill=(*accent, 28))
    draw.ellipse((-280, height - 760, 520, height + 80), fill=(*accent, 18))
    draw.rectangle((0, 0, 18, height), fill=(*accent, 255))

    kicker_font = _font(FONT_MEDIUM, 36)
    title_font = _font(FONT_BOLD, 52)
    body_font = _font(FONT_BOLD, 64 if role in {"hook", "closer"} else 56)
    meta_font = _font(FONT_REGULAR, 30)
    draw.text((80, 96), channel.name.upper(), font=kicker_font, fill=accent)
    draw.text((80, 156), topic_title, font=title_font, fill=muted)
    labels = {"hook": "AÇILIŞ", "fact": f"GERÇEK {index}", "closer": "KAPANIS", "cta": "ABONE OL"}
    draw.text((80, 240), labels.get(role, role.upper()), font=meta_font, fill=accent)

    lines = wrap_text(draw, text, body_font, width - 160)
    line_height = 84 if role in {"hook", "closer"} else 76
    y = max(360, (height - len(lines) * line_height) // 2 - 40)
    for line in lines:
        draw.text((80, y), line, font=body_font, fill=ink)
        y += line_height

    bar_y = height - 140
    draw.rounded_rectangle((80, bar_y, width - 80, bar_y + 10), radius=6, fill=(*muted, 70))
    draw.rounded_rectangle((80, bar_y, 80 + int((width - 160) * max(0.08, index / max(total, 1))), bar_y + 10), radius=6, fill=accent)
    draw.text((80, bar_y + 28), channel.tagline, font=meta_font, fill=muted)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.filter(ImageFilter.SMOOTH).convert("RGB").save(output, "PNG")
    return output


def render_thumbnail(channel: ChannelConfig, title: str, hook: str, output: Path) -> Path:
    width, height = 1280, 720
    primary, accent, ink = map(_hex, (channel.brand.primary, channel.brand.accent, channel.brand.text))
    image = Image.new("RGBA", (width, height), (*primary, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, 28, height), fill=(*accent, 255))
    draw.ellipse((width - 520, -180, width + 80, 420), fill=(*accent, 40))
    kicker_font, title_font, hook_font = _font(FONT_MEDIUM, 28), _font(FONT_BOLD, 72), _font(FONT_BOLD, 36)
    draw.text((72, 56), channel.name.upper(), font=kicker_font, fill=accent)
    y = 150
    for line in wrap_text(draw, title, title_font, width - 160)[:3]:
        draw.text((72, y), line, font=title_font, fill=ink)
        y += 84
    for line in wrap_text(draw, hook, hook_font, width - 200)[:2]:
        draw.text((72, y), line, font=hook_font, fill=(*ink, 210))
        y += 48
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, "PNG")
    return output
