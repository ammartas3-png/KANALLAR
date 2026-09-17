#!/usr/bin/env python3
"""Cheap local codebase index so agents do not reread the whole tree."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", "node_modules", "__pycache__", "data", "content", "logs"}


def symbols(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    found = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.append(node.name)
    return found


def main() -> None:
    index = []
    for path in ROOT.rglob("*.py"):
        if any(part in SKIP for part in path.parts):
            continue
        rel = str(path.relative_to(ROOT))
        index.append({"file": rel, "symbols": symbols(path)})
    out = ROOT / "memory" / "index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"files": index, "count": len(index)}, indent=2), encoding="utf-8")
    print(f"indexed {len(index)} files → {out}")


if __name__ == "__main__":
    main()
