from __future__ import annotations

from collections import defaultdict

from automation.logging import log_agent
from database.models import AnalyticsSnapshot, Experiment
from database.session import get_session
from memory.store import remember


@log_agent("DirectorAgent")
def learn(channel_id: str, **kwargs) -> dict:
    notes: list[str] = []
    with get_session() as session:
        experiments = session.query(Experiment).all()
        snapshots = session.query(AnalyticsSnapshot).all()
        views_by_video = defaultdict(int)
        for snap in snapshots:
            views_by_video[snap.video_id] = max(views_by_video[snap.video_id], snap.views)
        hook_scores: dict[str, list[int]] = defaultdict(list)
        duration_scores: dict[str, list[int]] = defaultdict(list)
        for exp in experiments:
            views = views_by_video.get(exp.video_id, 0)
            hook_scores[exp.hook_type].append(views)
            bucket = "20-25" if 20 <= exp.duration <= 25 else "other"
            duration_scores[bucket].append(views)
        for hook, values in hook_scores.items():
            avg = sum(values) / max(len(values), 1)
            notes.append(f"hook:{hook} avg_views={avg:.1f}|{'win' if avg >= 1 else 'lose'}")
        for bucket, values in duration_scores.items():
            avg = sum(values) / max(len(values), 1)
            notes.append(f"duration:{bucket} avg_views={avg:.1f}")
    for note in notes:
        if note.startswith("hook:"):
            hook, _, rest = note.partition(" ")
            kind = "winning_hooks" if note.endswith("|win") else "losing_hooks"
            remember(channel_id, kind, hook.split(":")[1], rest.replace("|win", "").replace("|lose", ""), 0.4)
        elif note.startswith("duration:"):
            remember(channel_id, "winning_duration", note.split(":")[1].split()[0], note, 0.3)
    if not notes:
        notes.append("Henüz YouTube analitiği yok. Üretim devam ediyor, öğrenme sonraki snapshot'ta başlar.")
    return {"notes": notes, "token_usage": 0, "api_cost": 0}
