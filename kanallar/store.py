from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kanallar.paths import db_path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class Job:
    id: str
    channel_id: str
    topic_id: str
    title: str
    status: str
    step: str
    error: str
    created_at: str
    updated_at: str
    video_path: str
    thumb_path: str
    audio_path: str
    script_json: str
    youtube_id: str
    youtube_url: str

    def script(self) -> dict[str, Any]:
        return json.loads(self.script_json) if self.script_json else {}

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "id": self.id,
            "channel_id": self.channel_id,
            "topic_id": self.topic_id,
            "title": self.title,
            "status": self.status,
            "step": self.step,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "youtube_id": self.youtube_id,
            "youtube_url": self.youtube_url,
            "has_video": bool(self.video_path),
            "has_thumb": bool(self.thumb_path),
        }
        payload.update(self.script())
        return payload


class Store:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    topic_id TEXT NOT NULL,
                    title TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    step TEXT NOT NULL DEFAULT '',
                    error TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    video_path TEXT NOT NULL DEFAULT '',
                    thumb_path TEXT NOT NULL DEFAULT '',
                    audio_path TEXT NOT NULL DEFAULT '',
                    script_json TEXT NOT NULL DEFAULT '',
                    youtube_id TEXT NOT NULL DEFAULT '',
                    youtube_url TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conn.commit()

    def used_topic_ids(self, channel_id: str) -> set[str]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT topic_id FROM jobs WHERE channel_id = ? AND status != 'failed'",
                (channel_id,),
            ).fetchall()
        return {row["topic_id"] for row in rows}

    def create_job(self, job_id: str, channel_id: str, topic_id: str, title: str) -> Job:
        now = utc_now()
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs (id, channel_id, topic_id, title, status, step, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'queued', 'queued', ?, ?)
                """,
                (job_id, channel_id, topic_id, title, now, now),
            )
            conn.commit()
        return self.get(job_id)

    def update(self, job_id: str, **fields: Any) -> Job:
        if not fields:
            return self.get(job_id)
        fields["updated_at"] = utc_now()
        assignments = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values()) + [job_id]
        with self._lock, self._connect() as conn:
            conn.execute(f"UPDATE jobs SET {assignments} WHERE id = ?", values)
            conn.commit()
        return self.get(job_id)

    def get(self, job_id: str) -> Job:
        with self._lock, self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return Job(**dict(row))

    def list_jobs(self, channel_id: str | None = None, limit: int = 40) -> list[Job]:
        query = "SELECT * FROM jobs"
        params: list[Any] = []
        if channel_id:
            query += " WHERE channel_id = ?"
            params.append(channel_id)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._lock, self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [Job(**dict(row)) for row in rows]

    def counts(self) -> dict[str, int]:
        with self._lock, self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) AS n FROM jobs").fetchone()["n"]
            ready = conn.execute(
                "SELECT COUNT(*) AS n FROM jobs WHERE status IN ('ready', 'uploaded')"
            ).fetchone()["n"]
            uploaded = conn.execute(
                "SELECT COUNT(*) AS n FROM jobs WHERE status = 'uploaded'"
            ).fetchone()["n"]
        return {"jobs": total, "ready": ready, "uploaded": uploaded}
