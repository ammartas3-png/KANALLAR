from __future__ import annotations

import json
import subprocess
from pathlib import Path


class RenderError(RuntimeError):
    pass


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RenderError(result.stderr[-2000:] or result.stdout[-2000:] or "ffmpeg hata verdi")


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def audio_duration(path: Path) -> float:
    data = probe(path)
    return float(data["format"]["duration"])


def scene_durations(texts: list[str], total: float) -> list[float]:
    weights = [max(len(text), 12) for text in texts]
    mass = sum(weights) or 1
    raw = [total * (weight / mass) for weight in weights]
    if raw:
        raw[-1] = max(0.8, total - sum(raw[:-1]))
    return [max(1.2, value) for value in raw]


def normalize_audio(src: Path, dest: Path) -> Path:
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar",
            "44100",
            str(dest),
        ]
    )
    return dest


def detect_black(path: Path) -> list[str]:
    result = subprocess.run(
        ["ffmpeg", "-i", str(path), "-vf", "blackdetect=d=0.4:pix_th=0.10", "-an", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    text = result.stderr or ""
    return [line for line in text.splitlines() if "black_start" in line]


def detect_silence(path: Path) -> list[str]:
    result = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "silencedetect=n=-40dB:d=1.2", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    text = result.stderr or ""
    return [line for line in text.splitlines() if "silence_start" in line]


def validate_short(path: Path) -> dict:
    data = probe(path)
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    width = int(video.get("width") or 0) if video else 0
    height = int(video.get("height") or 0) if video else 0
    duration = float(data.get("format", {}).get("duration") or 0)
    return {
        "width": width,
        "height": height,
        "duration": duration,
        "has_video": video is not None,
        "has_audio": audio is not None,
        "is_9_16": height > 0 and abs((width / height) - (9 / 16)) < 0.03,
        "is_1080x1920": width == 1080 and height == 1920,
        "size_bytes": int(data.get("format", {}).get("size") or 0),
        "black_segments": detect_black(path),
        "silence_segments": detect_silence(path),
    }
