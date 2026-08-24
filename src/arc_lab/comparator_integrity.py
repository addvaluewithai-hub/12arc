from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def derive_task_candidate_coverage(result: Mapping[str, Any]) -> dict[str, bool]:
    """Derive task-level candidate coverage only from persisted candidate correctness.

    A task is covered iff every test case has a parsed candidate stage and at least
    one persisted candidate marked candidate_correct. Missing/partial evidence is
    conservatively uncovered rather than inferred from summary annotations.
    """
    coverage: dict[str, bool] = {}
    for record in result.get("records", []):
        task_id = record["task_id"]
        tests = record.get("tests", [])
        coverage[task_id] = bool(tests) and all(
            test.get("candidate_stage", {}).get("parsed") is True
            and any(candidate.get("candidate_correct") is True for candidate in test.get("candidates", []))
            for test in tests
        )
    return coverage


def load_task_candidate_coverage(path: Path) -> dict[str, bool]:
    return derive_task_candidate_coverage(json.loads(path.read_text()))


def assert_annotations_match(
    comparator_coverage: Mapping[str, bool], annotations: Mapping[str, bool]
) -> None:
    """Reject manual comparator labels that disagree with durable evidence."""
    unknown = sorted(set(annotations) - set(comparator_coverage))
    mismatches = sorted(
        task_id
        for task_id, annotated in annotations.items()
        if task_id in comparator_coverage and bool(annotated) != comparator_coverage[task_id]
    )
    if unknown or mismatches:
        parts = []
        if unknown:
            parts.append("unknown task ids: " + ", ".join(unknown))
        if mismatches:
            parts.append("coverage mismatches: " + ", ".join(mismatches))
        raise ValueError("Comparator integrity failure: " + "; ".join(parts))


def coverage_delta(
    comparator_coverage: Mapping[str, bool], treatment_coverage: Mapping[str, bool]
) -> dict[str, list[str]]:
    """Mechanically compute new coverage and regressions on matched task IDs."""
    if set(comparator_coverage) != set(treatment_coverage):
        raise ValueError("Comparator and treatment task sets differ")
    new = sorted(t for t in comparator_coverage if not comparator_coverage[t] and treatment_coverage[t])
    regressions = sorted(t for t in comparator_coverage if comparator_coverage[t] and not treatment_coverage[t])
    return {"new_covered_task_ids": new, "regressed_task_ids": regressions}
