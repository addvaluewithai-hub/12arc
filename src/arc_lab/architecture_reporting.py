from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .comparator_integrity import coverage_delta, derive_task_candidate_coverage


def build_candidate_coverage_report(
    *,
    comparator_result_path: Path,
    treatment_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Build task-level architecture deltas only from durable candidate evidence.

    Comparator coverage is always loaded from a referenced persisted result. There
    is deliberately no argument for manually supplied baseline coverage flags.
    Treatment coverage is likewise derived from its candidate_correct records.
    """
    comparator_result = json.loads(comparator_result_path.read_text())
    comparator_coverage = derive_task_candidate_coverage(comparator_result)
    treatment_coverage = derive_task_candidate_coverage(treatment_result)
    delta = coverage_delta(comparator_coverage, treatment_coverage)
    return {
        "comparator_result": str(comparator_result_path),
        "comparator_candidate_coverage": comparator_coverage,
        "treatment_candidate_coverage": treatment_coverage,
        **delta,
    }


def persist_candidate_coverage_report(
    *,
    comparator_result_path: Path,
    treatment_result: Mapping[str, Any],
    output_path: Path,
) -> dict[str, Any]:
    """Persist an integrity-checked architecture coverage report atomically enough
    for experiment runners: validation happens before the output file is written.
    """
    report = build_candidate_coverage_report(
        comparator_result_path=comparator_result_path,
        treatment_result=treatment_result,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report
