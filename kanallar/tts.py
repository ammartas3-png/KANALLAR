from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path

from kanallar.config import ChannelConfig


class NarrationError(RuntimeError):
    pass


def synthesize(text: str, output: Path, channel: ChannelConfig) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        _edge_tts(text, output, channel.voice, channel.voice_rate)
        return output
    except Exception as edge_error:
        fallback = shutil.which("espeak-ng") or shutil.which("espeak")
        if not fallback:
            raise NarrationError(
                f"Ses üretilemedi ({edge_error}). edge-tts veya espeak-ng gerekli."
            ) from edge_error
        _espeak(text, output, fallback, channel.language)
        return output


def _edge_tts(text: str, output: Path, voice: str, rate: str) -> None:
    import edge_tts

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
        await communicate.save(str(output))

    asyncio.run(_run())
    if not output.exists() or output.stat().st_size < 1000:
        raise NarrationError("edge-tts boş ses dosyası üretti.")


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
