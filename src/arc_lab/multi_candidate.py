from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any, Mapping, Sequence

from . import lattice_region, rule_first
from .taskio import Grid, validate_grid


@dataclass(frozen=True)
class CandidateProvenance:
    candidate_id: str
    phase: str
    parent_candidate_id: str | None = None
    critique_id: str | None = None
    generation_attempt: int | None = None


@dataclass(frozen=True)
class AccountingRecord:
    request_count: int = 0
    cache_hits: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    runtime_seconds: float = 0.0
    provider_failures: int = 0
    parse_failures: int = 0


def canonical_program(program: str | Mapping[str, Any]) -> dict[str, Any]:
    """Parse a supported program and return its normalized fail-closed representation."""
    raw = json.loads(program) if isinstance(program, str) else dict(program)
    version = raw.get("schema_version")
    if version == rule_first.SCHEMA_VERSION:
        return rule_first.parse_program(raw)
    if version == lattice_region.SCHEMA_VERSION:
        return lattice_region.parse_program(raw)
    raise ValueError(f"unsupported candidate schema_version: {version!r}")


def canonical_json(program: str | Mapping[str, Any]) -> str:
    return json.dumps(canonical_program(program), sort_keys=True, separators=(",", ":"))


def program_fingerprint(program: str | Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(program).encode()).hexdigest()


def deduplicate_programs(programs: Sequence[str | Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Preserve first occurrence of each normalized IR program."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for raw in programs:
        normalized = canonical_program(raw)
        key = program_fingerprint(normalized)
        if key in seen:
            continue
        seen.add(key)
        out.append(normalized)
    return out


def execute_candidate(program: Mapping[str, Any], input_grid: Grid) -> Grid:
    version = program.get("schema_version")
    if version == rule_first.SCHEMA_VERSION:
        return rule_first.execute_program(program, input_grid)
    if version == lattice_region.SCHEMA_VERSION:
        return lattice_region.execute_program(program, input_grid)
    raise ValueError("unsupported candidate schema")


def _cell_error(predicted: Grid, expected: Grid) -> tuple[int, bool]:
    predicted = validate_grid(predicted)
    expected = validate_grid(expected)
    shape_match = len(predicted) == len(expected) and len(predicted[0]) == len(expected[0])
    if not shape_match:
        # A deterministic penalty larger than any legal ARC grid cell count.
        return 1000 + abs(len(predicted) - len(expected)) * 30 + abs(len(predicted[0]) - len(expected[0])), False
    return sum(a != b for prow, erow in zip(predicted, expected) for a, b in zip(prow, erow)), True


def _uniform_line_signature(grid: Grid) -> tuple[tuple[int, ...], tuple[int, ...]]:
    grid = validate_grid(grid)
    rows = tuple(i for i, row in enumerate(grid) if len(set(row)) == 1)
    cols = tuple(j for j in range(len(grid[0])) if len({row[j] for row in grid}) == 1)
    return rows, cols


def score_candidate(program: str | Mapping[str, Any], training_pairs: Sequence[Mapping[str, Grid]]) -> dict[str, Any]:
    normalized = canonical_program(program)
    if not training_pairs:
        raise ValueError("training_pairs must be non-empty")
    pair_records: list[dict[str, Any]] = []
    total_error = 0
    exact_pairs = 0
    structural_violations = 0
    for pair_index, pair in enumerate(training_pairs):
        input_grid = validate_grid(pair["input"])
        expected = validate_grid(pair["output"])
        try:
            predicted = execute_candidate(normalized, input_grid)
            errors, shape_match = _cell_error(predicted, expected)
            exact = shape_match and errors == 0
            if exact:
                exact_pairs += 1
            total_error += errors
            separator_preserved = _uniform_line_signature(predicted) == _uniform_line_signature(input_grid)
            if not separator_preserved:
                structural_violations += 1
            pair_records.append({
                "pair_index": pair_index,
                "parse_success": True,
                "execution_success": True,
                "shape_match": shape_match,
                "cell_error": errors,
                "exact": exact,
                "separator_preserved": separator_preserved,
                "failure": None,
            })
        except Exception as exc:
            structural_violations += 1
            total_error += 10000
            pair_records.append({
                "pair_index": pair_index,
                "parse_success": True,
                "execution_success": False,
                "shape_match": False,
                "cell_error": 10000,
                "exact": False,
                "separator_preserved": False,
                "failure": f"{type(exc).__name__}: {exc}",
            })
    canonical = canonical_json(normalized)
    return {
        "candidate_id": program_fingerprint(normalized),
        "program": normalized,
        "normalized_ir": canonical,
        "program_cost": len(canonical),
        "training_pair_count": len(training_pairs),
        "exact_training_pairs": exact_pairs,
        "exact_training_consistent": exact_pairs == len(training_pairs),
        "total_cell_error": total_error,
        "structural_violations": structural_violations,
        "pairs": pair_records,
    }


def rank_scored_candidates(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Deterministic selector. Model confidence/critique never enters ranking."""
    copied = [dict(record) for record in records]
    return sorted(
        copied,
        key=lambda r: (
            -int(bool(r["exact_training_consistent"])),
            -int(r["exact_training_pairs"]),
            int(r["total_cell_error"]),
            int(r["structural_violations"]),
            int(r["program_cost"]),
            str(r["candidate_id"]),
        ),
    )


def verify_candidate_batch(
    programs: Sequence[str | Mapping[str, Any]], training_pairs: Sequence[Mapping[str, Grid]]
) -> dict[str, Any]:
    parse_failures: list[dict[str, Any]] = []
    parsed: list[dict[str, Any]] = []
    for index, raw in enumerate(programs):
        try:
            parsed.append(canonical_program(raw))
        except Exception as exc:
            parse_failures.append({"index": index, "failure": f"{type(exc).__name__}: {exc}"})
    unique = deduplicate_programs(parsed)
    scored = [score_candidate(program, training_pairs) for program in unique]
    ranked = rank_scored_candidates(scored)
    return {
        "submitted_candidates": len(programs),
        "parseable_candidates": len(parsed),
        "parse_failures": parse_failures,
        "unique_candidates": len(unique),
        "duplicate_candidates": len(parsed) - len(unique),
        "ranked_candidates": ranked,
        "best_candidate_id": ranked[0]["candidate_id"] if ranked else None,
    }


def validate_provenance(records: Sequence[CandidateProvenance]) -> list[dict[str, Any]]:
    """Validate critique/repair ancestry without treating critique text as evidence."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for record in records:
        if not record.candidate_id or record.candidate_id in seen:
            raise ValueError("candidate provenance IDs must be unique and non-empty")
        if record.phase not in {"generate", "repair"}:
            raise ValueError("candidate provenance phase must be generate or repair")
        if record.phase == "repair" and (not record.parent_candidate_id or not record.critique_id):
            raise ValueError("repair provenance requires parent_candidate_id and critique_id")
        if record.parent_candidate_id and record.parent_candidate_id not in seen:
            raise ValueError("repair parent must precede child")
        seen.add(record.candidate_id)
        out.append(asdict(record))
    return out


def merge_accounting(records: Sequence[AccountingRecord]) -> dict[str, Any]:
    totals = AccountingRecord(
        request_count=sum(r.request_count for r in records),
        cache_hits=sum(r.cache_hits for r in records),
        input_tokens=sum(r.input_tokens for r in records),
        output_tokens=sum(r.output_tokens for r in records),
        total_tokens=sum(r.total_tokens for r in records),
        runtime_seconds=sum(r.runtime_seconds for r in records),
        provider_failures=sum(r.provider_failures for r in records),
        parse_failures=sum(r.parse_failures for r in records),
    )
    if min(asdict(totals).values()) < 0:
        raise ValueError("accounting values must be non-negative")
    return asdict(totals)
