"""Browser-use abstraction. MVP is not allowed to depend on browser-use."""

from __future__ import annotations


class BrowserResearch:
    enabled = False

    def search(self, query: str) -> list[dict]:
        raise RuntimeError(
            "Browser automation ikinci aşama. MVP resmi API + katalog + Wikipedia kullanır."
        )
