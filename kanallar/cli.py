from __future__ import annotations

import argparse
import json
import os
import sys

from kanallar.config import list_channels
from kanallar.pipeline import produce, publish
from kanallar.store import Store
from kanallar.youtube_upload import credentials_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kanallar", description="Otomasyonlu YouTube stüdyosu")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("channels", help="Kanal listesi")
    produce_p = sub.add_parser("produce", help="Bir video üret")
    produce_p.add_argument("channel")
    produce_p.add_argument("--topic", dest="topic_id")
    produce_p.add_argument("--upload", action="store_true")

    upload_p = sub.add_parser("upload", help="Hazır videoyu YouTube'a gönder")
    upload_p.add_argument("job_id")

    jobs_p = sub.add_parser("jobs", help="İş listesi")
    jobs_p.add_argument("--channel")

    studio = sub.add_parser("studio", help="Stüdyo arayüzünü aç")
    studio.add_argument("--host", default=os.environ.get("KANALLAR_HOST", "127.0.0.1"))
    studio.add_argument("--port", type=int, default=int(os.environ.get("KANALLAR_PORT", "8080")))

    args = parser.parse_args(argv)
    if args.command == "channels":
        for channel in list_channels():
            print(f"{channel.id:20} {channel.name}  [{channel.niche}/{channel.format}]  {channel.voice}")
        return 0
    if args.command == "jobs":
        for job in Store().list_jobs(args.channel):
            print(f"{job.id}  {job.status:10}  {job.channel_id:18}  {job.title}")
        return 0
    if args.command == "produce":
        result = produce(args.channel, topic_id=args.topic_id, upload=args.upload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.command == "upload":
        if not credentials_status()["client_secrets"]:
            print("client_secret.json yok. .env.example dosyasına bakın.", file=sys.stderr)
            return 2
        result = publish(args.job_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.command == "studio":
        import uvicorn
        from kanallar.web.app import app

        uvicorn.run(app, host=args.host, port=args.port)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
