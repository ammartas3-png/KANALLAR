from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path

from channels.loader import ChannelConfig


class NarrationError(RuntimeError):
    pass


def synthesize(text: str, output: Path, channel: ChannelConfig) -> str:
    """Provider-independent TTS. Paid engines plug in behind the same interface."""
    output.parent.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    preferred = (channel.voice.provider or "auto").lower()
    order = ["edge", "gtts", "espeak"]
    if preferred in {"elevenlabs", "openai", "google"}:
        errors.append(f"{preferred}: anahtar yok, ücretsiz yola düşülüyor")
    elif preferred in order:
        order = [preferred, *[item for item in order if item != preferred]]

    engines = {"edge": _edge_tts, "gtts": _gtts, "espeak": _espeak}
    for name in order:
        try:
            engines[name](text, output, channel)
            return {"edge": "edge-tts", "gtts": "gtts", "espeak": "espeak-ng"}[name]
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    raise NarrationError("Ses üretilemedi. " + " | ".join(errors))


def _edge_tts(text: str, output: Path, channel: ChannelConfig) -> None:
    import edge_tts

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, voice=channel.voice.voice, rate=channel.voice.rate)
        await communicate.save(str(output))

    asyncio.run(_run())
    _assert_audio(output, "edge-tts")


def _gtts(text: str, output: Path, channel: ChannelConfig) -> None:
    from gtts import gTTS

    lang = "tr" if channel.language.startswith("tr") else channel.language.split("-")[0]
    gTTS(text=text, lang=lang, slow=False).save(str(output))
    _assert_audio(output, "gtts")


def _espeak(text: str, output: Path, channel: ChannelConfig) -> None:
    binary = shutil.which("espeak-ng") or shutil.which("espeak")
    if not binary:
        raise NarrationError("espeak-ng yok")
    wav = output.with_suffix(".wav")
    lang = "tr" if channel.language.startswith("tr") else "en"
    subprocess.run([binary, "-v", lang, "-s", "145", "-w", str(wav), text], check=True, capture_output=True, text=True)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-qscale:a", "4", str(output)],
        check=True,
        capture_output=True,
        text=True,
    )
    wav.unlink(missing_ok=True)
    _assert_audio(output, "espeak-ng")


def _assert_audio(output: Path, engine: str) -> None:
    if not output.exists() or output.stat().st_size < 400:
        raise NarrationError(f"{engine} boş ses dosyası üretti.")
