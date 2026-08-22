from __future__ import annotations

import hashlib
import json

DEFAULT_SEED = "arc-lab-v1"
SPLIT_NAMES = ("dev_train", "dev_validation", "dev_holdout")


def bucket(task_id: str, seed: str = DEFAULT_SEED) -> int:
    digest = hashlib.sha256(f"{seed}:{task_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % 100


def split_name(task_id: str, seed: str = DEFAULT_SEED) -> str:
    value = bucket(task_id, seed)
    if value < 70:
        return "dev_train"
    if value < 90:
        return "dev_validation"
    return "dev_holdout"


def partition(task_ids: list[str], seed: str = DEFAULT_SEED) -> dict[str, list[str]]:
    if len(task_ids) != len(set(task_ids)):
        raise ValueError("task ids must be unique")
    result = {name: [] for name in SPLIT_NAMES}
    for task_id in sorted(task_ids):
        result[split_name(task_id, seed)].append(task_id)
    return result


def build_split_manifest(
    task_ids: list[str],
    *,
    seed: str = DEFAULT_SEED,
    dataset: str = "ARC-AGI-2 public training",
    source_commit: str | None = None,
) -> dict:
    splits = partition(task_ids, seed)
    payload = {
        "schema_version": 1,
        "dataset": dataset,
        "seed": seed,
        "task_count": len(task_ids),
        "counts": {name: len(splits[name]) for name in SPLIT_NAMES},
        "splits": splits,
    }
    if source_commit is not None:
        payload["source_commit"] = source_commit
    payload["manifest_sha256"] = manifest_digest(payload)
    return payload


def manifest_digest(manifest: dict) -> str:
    payload = dict(manifest)
    payload.pop("manifest_sha256", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()
