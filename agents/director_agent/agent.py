from __future__ import annotations

from collections import defaultdict
from statistics import median

from automation.logging import log_agent
from database.models import AnalyticsSnapshot, Experiment, Video
from database.session import get_session
from memory.store import remember

MIN_SAMPLES = 2


def score_groups(groups: dict[str, list[int]], channel_median: float) -> dict[str, dict]:
    """Each group's mean views relative to the channel median (1.0 = typical video)."""
    scored = {}
    for name, values in groups.items():
        avg = sum(values) / len(values)
        relative = avg / channel_median if channel_median > 0 else 0.0
        if len(values) < MIN_SAMPLES or channel_median <= 0:
            verdict = "insufficient"
        else:
            verdict = "win" if relative > 1.0 else "lose"
        scored[name] = {"avg": avg, "relative": relative, "samples": len(values), "verdict": verdict}
    return scored


@log_agent("DirectorAgent")
def learn(channel_id: str, **kwargs) -> dict:
    notes: list[str] = []
    with get_session() as session:
        rows = (
            session.query(Experiment)
            .join(Video, Video.id == Experiment.video_id)
            .filter(Video.channel_id == channel_id)
            .all()
        )
        video_ids = {exp.video_id for exp in rows}
        views_by_video: dict[str, int] = defaultdict(int)
        if video_ids:
            for snap in session.query(AnalyticsSnapshot).filter(AnalyticsSnapshot.video_id.in_(video_ids)):
                views_by_video[snap.video_id] = max(views_by_video[snap.video_id], snap.views)
        hook_groups: dict[str, list[int]] = defaultdict(list)
        duration_groups: dict[str, list[int]] = defaultdict(list)
        for exp in rows:
            if exp.video_id not in views_by_video:
                continue
            views = views_by_video[exp.video_id]
            hook_groups[exp.hook_type or "unknown"].append(views)
            bucket = "20-45" if 20 <= exp.duration <= 45 else "other"
            duration_groups[bucket].append(views)
    channel_median = float(median(views_by_video.values())) if views_by_video else 0.0
    for hook, s in score_groups(hook_groups, channel_median).items():
        notes.append(f"hook:{hook} rel={s['relative']:.2f} n={s['samples']}")
        if s["verdict"] in {"win", "lose"}:
            kind = "winning_hooks" if s["verdict"] == "win" else "losing_hooks"
            remember(channel_id, kind, hook, f"rel={s['relative']:.2f} n={s['samples']}", 0.4)
    for bucket, s in score_groups(duration_groups, channel_median).items():
        notes.append(f"duration:{bucket} rel={s['relative']:.2f} n={s['samples']}")
        if s["verdict"] == "win":
            remember(channel_id, "winning_duration", bucket, f"rel={s['relative']:.2f} n={s['samples']}", 0.3)
    if not notes:
        notes.append("Henüz YouTube analitiği yok. Üretim devam ediyor, öğrenme sonraki snapshot'ta başlar.")
    return {"notes": notes, "channel_median_views": channel_median, "token_usage": 0, "api_cost": 0}
