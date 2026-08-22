from __future__ import annotations

import hashlib

DEFAULT_SEED = "arc-lab-v1"


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
    result = {"dev_train": [], "dev_validation": [], "dev_holdout": []}
    for task_id in sorted(task_ids):
        result[split_name(task_id, seed)].append(task_id)
    return result
