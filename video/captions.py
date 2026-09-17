from __future__ import annotations

from pathlib import Path
import re


def tokenize(text: str) -> list[str]:
    return [part for part in re.findall(r"\S+", text) if part]


def word_timings(text: str, duration: float) -> list[dict]:
    words = tokenize(text)
    if not words:
        return []
    weights = [max(len(word), 2) for word in words]
    mass = sum(weights)
    cursor = 0.0
    rows = []
    for word, weight in zip(words, weights, strict=True):
        span = duration * (weight / mass)
        rows.append({"word": word, "start": cursor, "end": cursor + span})
        cursor += span
    if rows:
        rows[-1]["end"] = duration
    return rows


def chunk_words(timings: list[dict], max_words: int = 4) -> list[list[dict]]:
    return [timings[i : i + max_words] for i in range(0, len(timings), max_words)]


def _ts(seconds: float) -> str:
    millis = int(round(max(seconds, 0) * 100))
    hours, rem = divmod(millis, 360000)
    minutes, rem = divmod(rem, 6000)
    secs, cs = divmod(rem, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def build_ass(text: str, duration: float, output: Path, accent: str = "#F4B942") -> Path:
    """Word-level ASS captions, 2-4 words on screen, safe-zone mid-lower third."""
    hex_color = accent.lstrip("#")
    ass_color = f"&H00{hex_color[4:6]}{hex_color[2:4]}{hex_color[0:2]}&"
    timings = word_timings(text, duration)
    chunks = chunk_words(timings, 4)
    events = []
    for chunk in chunks:
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        line = " ".join(
            (f"{{\\c{ass_color}}}{item['word']}{{\\c&H00FFFFFF&}}" if index == 0 else item["word"])
            for index, item in enumerate(chunk)
        )
        events.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},Kanallar,,0,0,0,,{line}")
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kanallar,Inter,64,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,1,6,0,2,70,70,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    return output
