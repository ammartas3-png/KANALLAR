from __future__ import annotations

import argparse
import json
import os

from analytics.queries import dashboard_stats
from automation.jobs import list_awaiting_approval, load_checkpoint
from automation.pipeline import approve_and_maybe_upload, produce, refresh_analytics, reject
from channels.loader import load_channel
from database.session import init_db
from media.router import status_report
from youtube.api import credentials_status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="kanallar", description="YouTube Shorts fabrikası")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("channel", help="Aktif MVP kanalı")
    produce_p = sub.add_parser("produce", help="Research → video → QA (varsayılan: onay bekler)")
    produce_p.add_argument("--topic")
    produce_p.add_argument("--upload", action="store_true", help="Onay kapısı kapalıysa yükle")
    produce_p.add_argument(
        "--force-upload",
        action="store_true",
        help="İnsan onayı kapısını atla (dikkatli kullan)",
    )
    produce_p.add_argument("--resume", help="Yarıda kalan video_id ile devam et")
    approve_p = sub.add_parser("approve", help="Onay beklemedeki videoyu onayla")
    approve_p.add_argument("--id", required=True)
    approve_p.add_argument("--upload", action="store_true", help="Onaydan sonra YouTube'a yükle")
    reject_p = sub.add_parser("reject", help="Videoyu reddet")
    reject_p.add_argument("--id", required=True)
    reject_p.add_argument("--reason", default="")
    sub.add_parser("pending", help="Onay bekleyen videolar")
    job_p = sub.add_parser("job", help="Checkpoint durumu")
    job_p.add_argument("--id", required=True)
    sub.add_parser("media-status", help="MediaProvider (local/kie/higgsfield) durumu")
    sub.add_parser("analytics", help="YouTube analitikleri (varsa)")
    sub.add_parser("dashboard-data", help="Özet JSON")
    studio = sub.add_parser("studio", help="Basit stüdyo")
    studio.add_argument("--host", default=os.environ.get("KANALLAR_HOST", "127.0.0.1"))
    studio.add_argument("--port", type=int, default=int(os.environ.get("KANALLAR_PORT", "8080")))
    args = parser.parse_args(argv)

    init_db()
    if args.command == "channel":
        channel = load_channel()
        print(json.dumps(channel.model_dump(), ensure_ascii=False, indent=2))
        print("youtube:", credentials_status())
        return 0
    if args.command == "produce":
        print(
            json.dumps(
                produce(
                    topic_id=args.topic,
                    upload=args.upload,
                    force_upload=args.force_upload,
                    resume_id=args.resume,
                ),
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        return 0
    if args.command == "approve":
        print(json.dumps(approve_and_maybe_upload(args.id, upload=args.upload), ensure_ascii=False, indent=2))
        return 0
    if args.command == "reject":
        print(json.dumps(reject(args.id, reason=args.reason), ensure_ascii=False, indent=2))
        return 0
    if args.command == "pending":
        print(json.dumps(list_awaiting_approval(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "job":
        print(json.dumps(load_checkpoint(args.id), ensure_ascii=False, indent=2))
        return 0
    if args.command == "media-status":
        print(json.dumps(status_report(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "analytics":
        print(json.dumps(refresh_analytics(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "dashboard-data":
        print(json.dumps(dashboard_stats(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "studio":
        import uvicorn
        from apps.studio.app import app

        uvicorn.run(app, host=args.host, port=args.port)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
