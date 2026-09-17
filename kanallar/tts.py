from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path

from kanallar.config import ChannelConfig


class NarrationError(RuntimeError):
    pass


def synthesize(text: str, output: Path, channel: ChannelConfig) -> str:
    """Write narration to output. Returns the engine name that succeeded."""
    output.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []

    try:
        _edge_tts(text, output, channel.voice, channel.voice_rate)
        return "edge-tts"
    except Exception as exc:
        errors.append(f"edge-tts: {exc}")

    try:
        _gtts(text, output, channel.language)
        return "gtts"
    except Exception as exc:
        errors.append(f"gtts: {exc}")

    fallback = shutil.which("espeak-ng") or shutil.which("espeak")
    if fallback:
        try:
            _espeak(text, output, fallback, channel.language)
            return "espeak-ng"
        except Exception as exc:
            errors.append(f"espeak-ng: {exc}")

    raise NarrationError("Ses üretilemedi. " + " | ".join(errors))


def _edge_tts(text: str, output: Path, voice: str, rate: str) -> None:
    import edge_tts

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
        await communicate.save(str(output))

    asyncio.run(_run())
    _assert_audio(output, "edge-tts")


def _gtts(text: str, output: Path, language: str) -> None:
    from gtts import gTTS

    lang = "tr" if language.startswith("tr") else language.split("-")[0]
    gTTS(text=text, lang=lang, slow=False).save(str(output))
    _assert_audio(output, "gtts")


def _espeak(text: str, output: Path, binary: str, language: str) -> None:
    wav = output.with_suffix(".wav")
    lang = "tr" if language.startswith("tr") else "en"
    subprocess.run(
        [binary, "-v", lang, "-s", "145", "-w", str(wav), text],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav),
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "4",
            str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    wav.unlink(missing_ok=True)
    _assert_audio(output, "espeak-ng")


def _assert_audio(output: Path, engine: str) -> None:
    if not output.exists() or output.stat().st_size < 400:
        raise NarrationError(f"{engine} boş ses dosyası üretti.")
