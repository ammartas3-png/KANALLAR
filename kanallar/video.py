from __future__ import annotations

import json
import subprocess
from pathlib import Path


class RenderError(RuntimeError):
    pass


def audio_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def scene_durations(texts: list[str], total: float) -> list[float]:
    weights = [max(len(text), 12) for text in texts]
    mass = sum(weights)
    raw = [total * (weight / mass) for weight in weights]
    # Keep the last scene from being clipped by encoder rounding.
    if raw:
        raw[-1] = max(0.8, total - sum(raw[:-1]))
    return [max(1.2, value) for value in raw]


def render_video(
    slides: list[Path],
    durations: list[float],
    audio: Path,
    output: Path,
    size: tuple[int, int],
) -> Path:
    if len(slides) != len(durations):
        raise RenderError("Sahne ve süre sayıları uyuşmuyor.")
    output.parent.mkdir(parents=True, exist_ok=True)
    work = output.parent / "clips"
    work.mkdir(parents=True, exist_ok=True)
    clips: list[Path] = []
    width, height = size

    for index, (slide, duration) in enumerate(zip(slides, durations, strict=True)):
        clip = work / f"clip_{index:02d}.mp4"
        frames = max(36, int(round(duration * 30)))
        zoom = (
            f"zoompan=z='min(1.0+0.0007*on,1.10)':d={frames}:x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30,format=yuv420p"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(slide),
            "-vf",
            zoom,
            "-t",
            f"{duration:.3f}",
            "-an",
            "-movflags",
            "+faststart",
            str(clip),
        ]
        _run(cmd)
        clips.append(clip)

    list_file = work / "concat.txt"
    list_file.write_text("".join(f"file '{clip.resolve()}'\n" for clip in clips), encoding="utf-8")
    silent = work / "silent.mp4"
    _run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(silent),
        ]
    )
    _run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent),
            "-i",
            str(audio),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ]
    )
    if not output.exists() or output.stat().st_size < 10_000:
        raise RenderError("Video dosyası üretilemedi.")
    return output


def _run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RenderError(result.stderr[-2000:] or result.stdout[-2000:] or "ffmpeg hata verdi.")
