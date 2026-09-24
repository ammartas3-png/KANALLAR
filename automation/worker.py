from __future__ import annotations

import logging
import threading

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from automation.bootstrap import bootstrap_cloud_secrets
from automation.pipeline import produce, refresh_analytics
from channels.loader import load_channel
from config.settings import get_settings
from database.session import init_db
from storage import storage_status

log = logging.getLogger("kanallar.worker")


def _parse_cron(expr: str) -> CronTrigger:
    parts = expr.split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron (need 5 fields): {expr}")
    minute, hour, day, month, day_of_week = parts
    return CronTrigger(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
        timezone="UTC",
    )


def run_studio_background() -> None:
    import uvicorn
    from apps.studio.app import app

    settings = get_settings()
    uvicorn.run(app, host=settings.kanallar_host, port=settings.kanallar_port, log_level="info")


def build_scheduler() -> BlockingScheduler:
    channel = load_channel()
    settings = get_settings()
    scheduler = BlockingScheduler(timezone="UTC")

    def _produce() -> None:
        log.info("Scheduled produce starting channel=%s", channel.id)
        try:
            result = produce(channel.id)
            log.info("Scheduled produce done id=%s status=%s", result.get("id"), result.get("status"))
        except Exception:  # noqa: BLE001
            log.exception("Scheduled produce failed")

    scheduler.add_job(_produce, _parse_cron(settings.worker_produce_cron), id="daily_produce")
    if settings.worker_analytics_hourly:
        scheduler.add_job(
            lambda: refresh_analytics("1h"),
            CronTrigger(minute=0, timezone="UTC"),
            id="analytics_hourly",
        )
        scheduler.add_job(
            lambda: refresh_analytics("24h"),
            CronTrigger(hour=7, minute=30, timezone="UTC"),
            id="analytics_daily",
        )
    return scheduler


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    settings = get_settings()
    boot = bootstrap_cloud_secrets()
    init_db()
    log.info(
        "Cloud worker starting run_mode=%s storage=%s youtube=%s",
        settings.run_mode,
        storage_status(),
        {k: boot[k] for k in ("client_secrets_from_env", "channel_tokens")},
    )
    if settings.worker_enable_studio:
        thread = threading.Thread(target=run_studio_background, name="studio", daemon=True)
        thread.start()
        log.info("Studio on %s:%s", settings.kanallar_host, settings.kanallar_port)
    scheduler = build_scheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
