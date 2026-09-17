from __future__ import annotations

import json
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from database.models import AgentRun
from database.session import get_session


def log_agent(agent_name: str) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            started = time.perf_counter()
            video_id = str(kwargs.get("video_id") or "")
            payload_in = kwargs.get("log_input") or {}
            tokens = 0
            cost = 0.0
            error = ""
            output: Any = None
            try:
                output = fn(*args, **kwargs)
                if isinstance(output, dict):
                    tokens = int(output.get("token_usage") or 0)
                    cost = float(output.get("api_cost") or 0)
                return output
            except Exception as exc:
                error = str(exc)
                raise
            finally:
                elapsed = int((time.perf_counter() - started) * 1000)
                with get_session() as session:
                    session.add(
                        AgentRun(
                            agent=agent_name,
                            video_id=video_id,
                            input_json=json.dumps(payload_in, ensure_ascii=False, default=str)[:8000],
                            output_json=json.dumps(output, ensure_ascii=False, default=str)[:8000]
                            if output is not None
                            else "{}",
                            duration_ms=elapsed,
                            token_usage=tokens,
                            api_cost=cost,
                            error=error,
                        )
                    )

        return wrapper

    return decorator
