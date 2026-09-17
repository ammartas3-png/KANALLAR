from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from config.paths import REMOTION_DIR


def remotion_available() -> bool:
    return (REMOTION_DIR / "package.json").exists() and shutil.which("npx") is not None


def render_with_remotion(props: dict, output: Path) -> Path:
    if not remotion_available():
        raise RuntimeError("Remotion projesi yok. apps/remotion altına kurulur.")
    output.parent.mkdir(parents=True, exist_ok=True)
    props_path = output.with_suffix(".props.json")
    props_path.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    result = subprocess.run(
        [
            "npx",
            "remotion",
            "render",
            "Shorts",
            str(output),
            f"--props={props_path}",
        ],
        cwd=REMOTION_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:] or "Remotion render başarısız")
    return output
