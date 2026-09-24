from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func

from database.models import AgentRun, AnalyticsSnapshot, Channel, Experiment, MemoryItem, Upload, Video
from database.session import get_session


def dashboard_stats() -> dict:
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week = now - timedelta(days=7)
    with get_session() as session:
        produced_today = session.query(Video).filter(Video.created_at >= start).count()
        published = session.query(Upload).filter(Upload.status == "uploaded").count()
        views_24h = (
            session.query(func.coalesce(func.sum(AnalyticsSnapshot.views), 0))
            .filter(AnalyticsSnapshot.collected_at >= now - timedelta(hours=24))
            .scalar()
        )
        views_7d = (
            session.query(func.coalesce(func.sum(AnalyticsSnapshot.views), 0))
            .filter(AnalyticsSnapshot.collected_at >= week)
            .scalar()
        )
        videos = session.query(Video).order_by(Video.created_at.desc()).limit(20).all()
        costs = [row.cost_per_video for row in videos]
        avg_cost = sum(costs) / len(costs) if costs else 0
        best = session.query(AnalyticsSnapshot).order_by(AnalyticsSnapshot.views.desc()).first()
        worst = (
            session.query(AnalyticsSnapshot)
            .filter(AnalyticsSnapshot.views > 0)
            .order_by(AnalyticsSnapshot.views.asc())
            .first()
        )
        hooks_win = session.query(MemoryItem).filter(MemoryItem.type == "winning_hooks").all()
        hooks_lose = session.query(MemoryItem).filter(MemoryItem.type == "losing_hooks").all()
        topics = session.query(Experiment.hook_type, func.count(Experiment.id)).group_by(Experiment.hook_type).all()
        channels = session.query(Channel).all()
        return {
            "channels": [{"id": c.id, "name": c.name, "niche": c.niche, "status": c.status} for c in channels],
            "produced_today": produced_today,
            "published": published,
            "views_24h": int(views_24h or 0),
            "views_7d": int(views_7d or 0),
            "subscribers": 0,
            "best_video": best.video_id if best else "",
            "worst_video": worst.video_id if worst else "",
            "average_video_cost": round(avg_cost, 4),
            "cost_per_1000_views": 0,
            "top_topics": [row[0] for row in topics if row[0]],
            "winning_hooks": [item.key for item in hooks_win],
            "failed_hooks": [item.key for item in hooks_lose],
            "videos": [
                {
                    "id": v.id,
                    "status": v.status,
                    "duration": v.duration,
                    "cost": v.cost_per_video,
                    "created_at": v.created_at.isoformat() if v.created_at else "",
                    "filepath": v.filepath,
                }
                for v in videos
            ],
            "agent_runs": session.query(AgentRun).count(),
        }
