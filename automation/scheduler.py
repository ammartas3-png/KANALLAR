from __future__ import annotations

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from automation.pipeline import produce, refresh_analytics
from channels.loader import load_channel


def build_scheduler() -> BlockingScheduler:
    channel = load_channel()
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(lambda: produce(channel.id), CronTrigger(hour=8, minute=0), id="daily_produce")
    scheduler.add_job(lambda: refresh_analytics("1h"), CronTrigger(minute=0), id="analytics_hourly")
    scheduler.add_job(lambda: refresh_analytics("24h"), CronTrigger(hour=7, minute=30), id="analytics_daily")
    return scheduler


def main() -> None:
    scheduler = build_scheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
