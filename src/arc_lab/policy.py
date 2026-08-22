from __future__ import annotations

from pathlib import Path

REQUIRED = [
    "lab/RUNNER.md",
    "lab/CHARTER.md",
    "lab/STATE.md",
    "lab/HANDOFF.md",
    "lab/config.json",
    "lab/registry/queue.json",
    "lab/protocols/LEAKAGE.md",
    "lab/protocols/EXPERIMENT-CONTRACT.md",
]


def validate_repository(root: str | Path = ".") -> list[str]:
    root = Path(root)
    missing = [path for path in REQUIRED if not (root / path).exists()]
    return missing
