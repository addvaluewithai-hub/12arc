from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .splits import DEFAULT_SEED, build_split_manifest, manifest_digest
from .taskio import validate_task_directory

TASK_ID_RE = re.compile(r"^[0-9a-f]{8}$")


def read_task_ids(path: str | Path) -> list[str]:
    raw = Path(path).read_text()
    ids = [line.strip() for line in raw.splitlines() if line.strip()]
    if not ids:
        raise ValueError("task id list is empty")
    if any(not TASK_ID_RE.fullmatch(task_id) for task_id in ids):
        raise ValueError("task id list contains an invalid id")
    if len(ids) != len(set(ids)):
        raise ValueError("task id list contains duplicates")
    return ids


def file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_split_manifest(
    ids_file: str | Path,
    output: str | Path,
    *,
    seed: str = DEFAULT_SEED,
    source_commit: str | None = None,
) -> dict:
    manifest = build_split_manifest(
        read_task_ids(ids_file), seed=seed, source_commit=source_commit
    )
    Path(output).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def verify_split_manifest(ids_file: str | Path, manifest_file: str | Path) -> None:
    actual = json.loads(Path(manifest_file).read_text())
    if actual.get("manifest_sha256") != manifest_digest(actual):
        raise ValueError("split manifest self-hash mismatch")
    expected = build_split_manifest(
        read_task_ids(ids_file),
        seed=actual["seed"],
        dataset=actual["dataset"],
        source_commit=actual.get("source_commit"),
    )
    if actual != expected:
        raise ValueError("split manifest does not match task id list")


def validate_development_dataset(
    training_dir: str | Path,
    *,
    expected_task_ids: list[str] | None = None,
) -> dict[str, int]:
    # Deliberately accepts only the training directory. There is no evaluation path
    # in the default development validation surface.
    summary = validate_task_directory(training_dir, require_test_outputs=True)
    if expected_task_ids is not None:
        actual = sorted(path.stem for path in Path(training_dir).glob("*.json"))
        if actual != sorted(expected_task_ids):
            raise ValueError("training directory task ids do not match expected ids")
    return summary
