from __future__ import annotations

from pathlib import Path

from channels.loader import ChannelConfig
from video.captions import build_ass
from video.ffmpeg import RenderError, audio_duration, normalize_audio, run, scene_durations
from video.slides import render_slide, render_thumbnail


def compose_short(channel: ChannelConfig, script: dict, audio: Path, work: Path) -> dict:
    work.mkdir(parents=True, exist_ok=True)
    scenes = script["scenes"]
    slides = []
    for index, scene in enumerate(scenes, start=1):
        slide = work / "slides" / f"{index:02d}.png"
        slide.parent.mkdir(parents=True, exist_ok=True)
        render_slide(channel, scene["text"], scene["role"], index, len(scenes), slide, script["topic"])
        slides.append(slide)
    thumb = render_thumbnail(channel, script["topic"], script["hook"], work / "thumbnail.png")
    clean_audio = normalize_audio(audio, work / "voice_norm.mp3")
    duration = audio_duration(clean_audio)
    durations = scene_durations([scene["text"] for scene in scenes], duration)
    ass = build_ass(script["narration"], duration, work / "captions.ass", channel.brand.accent)
    silent = _render_clips(slides, durations, work, channel.video_size)
    output = work / "final.mp4"
    ass_filter = f"ass={ass.resolve()}".replace("\\", "/").replace(":", "\\:")
    encode = [
        "ffmpeg",
        "-y",
        "-i",
        str(silent),
        "-i",
        str(clean_audio),
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
    captions_burned = True
    try:
        run(encode[:6] + ["-vf", ass_filter] + encode[6:])
    except RenderError:
        captions_burned = False
        run(encode)
    if not output.exists() or output.stat().st_size < 10_000:
        raise RenderError("Final Short üretilemedi")
    return {
        "video": output,
        "thumb": thumb,
        "captions": ass,
        "captions_burned": captions_burned,
        "duration": duration,
    }


def _render_clips(slides: list[Path], durations: list[float], work: Path, size: tuple[int, int]) -> Path:
    clips_dir = work / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    clips = []
    width, height = size
    for index, (slide, duration) in enumerate(zip(slides, durations, strict=True)):
        clip = clips_dir / f"clip_{index:02d}.mp4"
        frames = max(36, int(round(duration * 30)))
        zoom = (
            f"zoompan=z='min(1.0+0.0007*on,1.10)':d={frames}:x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':s={width}x{height}:fps=30,format=yuv420p"
        )
        run(["ffmpeg", "-y", "-loop", "1", "-i", str(slide), "-vf", zoom, "-t", f"{duration:.3f}", "-an", str(clip)])
        clips.append(clip)
    listing = clips_dir / "concat.txt"
    listing.write_text("".join(f"file '{clip.resolve()}'\n" for clip in clips), encoding="utf-8")
    silent = work / "silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(silent)])
    return silent
