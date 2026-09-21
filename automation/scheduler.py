from __future__ import annotations

"""Legacy scheduler entry — prefer `python -m automation.worker` for cloud."""

from automation.worker import build_scheduler, main

__all__ = ["build_scheduler", "main"]


if __name__ == "__main__":
    main()
