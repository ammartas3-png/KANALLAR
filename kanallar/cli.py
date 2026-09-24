from __future__ import annotations

import argparse
import json
import os
import sys

from automation.pipeline import produce
from channels.loader import load_channel
from youtube.api import credentials_status

MVP_ALIASES = {"channel_01", "bilim-dakikasi"}


def main(argv: list[str] | None = None) -> int:
    """Compatibility CLI. Canonical entry: python -m automation."""
    parser = argparse.ArgumentParser(prog="kanallar", description="YouTube Shorts fabrikası (uyumluluk)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("channels", help="Aktif MVP kanalı")
    produce_p = sub.add_parser("produce", help="Video üret")
    produce_p.add_argument("channel", nargs="?", default="channel_01")
    produce_p.add_argument("--topic", dest="topic_id")
    produce_p.add_argument("--upload", action="store_true")
    studio = sub.add_parser("studio", help="Stüdyo")
    studio.add_argument("--host", default=os.environ.get("KANALLAR_HOST", "127.0.0.1"))
    studio.add_argument("--port", type=int, default=int(os.environ.get("KANALLAR_PORT", "8080")))
    args = parser.parse_args(argv)

    if args.command == "channels":
        channel = load_channel()
        print(f"{channel.id:20} {channel.name}  [MVP]")
        return 0
    if args.command == "produce":
        alias = args.channel or "channel_01"
        if alias not in MVP_ALIASES:
            print("MVP tek kanal: channel_01 (eski ad: bilim-dakikasi)", file=sys.stderr)
            return 2
        result = produce(channel_id="channel_01", topic_id=args.topic_id, upload=args.upload)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return 0
    if args.command == "studio":
        import uvicorn
        from apps.studio.app import app

        print("youtube:", credentials_status())
        uvicorn.run(app, host=args.host, port=args.port)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
