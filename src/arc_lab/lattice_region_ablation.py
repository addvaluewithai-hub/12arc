from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .compact_hypothesis_search import GENERATION_CANDIDATES, MODEL, PROVIDER
from .lattice_region import parse_program, score_program_candidates
from .rule_first import matched_coverage_delta
from .target_model import CachedTargetClient, NvidiaNIMProvider, TargetRequest
from .taskio import load_task

TASK_IDS = ["0607ce86", "06df4c85"]
TASK_ID = "T0017-LATTICE-REGION-PRIMITIVE-ABLATION"
SOLVER_VERSION = "lattice-region-v2"


def candidate_prompt(task: dict[str, Any], test_input: list[list[int]]) -> str:
    return (
        "Solve this ARC task by proposing exactly three DISTINCT compact executable programs. "
        "Do NOT serialize any output grid. Return JSON only with key programs, a list of exactly three objects. "
        "Each program must use schema_version=2 and a non-empty steps list. "
        "Allowed ops are identity and lattice_peer_reduce. identity has only key op. "
        "lattice_peer_reduce has exactly keys op, axis, reduce, write. "
        "axis is one of all,row,col. reduce is one of majority,majority_nonbackground,first_nonbackground. "
        "write is one of all,background_only,outliers_only. "
        "The executor infers regular separator-defined cells from the input, compares corresponding relative positions across peer cells, "
        "infers background from the grid, applies the generic reducer/write condition, and reassembles while preserving separator lines. "
        "Do not use task IDs, absolute coordinates, task-specific color constants, or hand-entered target patterns. "
        "The programs will be executed deterministically after your response. No markdown.\n\n"
        "TRAINING:\n" + json.dumps(task["train"], separators=(",", ":")) +
        "\n\nTEST INPUT:\n" + json.dumps(test_input, separators=(",", ":"))
    )


def parse_programs(text: str) -> list[dict[str, Any]] | None:
    try:
        s = text.strip()
        start, end = s.find("{"), s.rfind("}")
        if start < 0 or end < start:
            return None
        obj = json.loads(s[start:end + 1])
        programs = obj.get("programs") if isinstance(obj, dict) else None
        if not isinstance(programs, list) or len(programs) != 3:
            return None
        parsed = [parse_program(p) for p in programs]
        if len({json.dumps(p, sort_keys=True, separators=(",", ":")) for p in parsed}) != 3:
            return None
        return parsed
    except Exception:
        return None


def _comparator_from_r030(path: Path) -> dict[str, bool]:
    baseline = json.loads(path.read_text())
    if baseline.get("task_id") != "T0015-RULE-FIRST-OVERFLOW-ABLATION":
        raise ValueError("comparator is not ARC-R030/T0015 evidence")
    if baseline.get("task_ids") != TASK_IDS:
        raise ValueError("comparator task IDs differ from frozen task set")
    coverage = baseline.get("treatment_coverage")
    if not isinstance(coverage, dict) or set(coverage) != set(TASK_IDS):
        raise ValueError("comparator coverage missing/mismatched")
    return {tid: bool(coverage[tid]) for tid in TASK_IDS}


def run(training_dir: Path, comparator_path: Path, cache_dir: Path, output: Path) -> dict[str, Any]:
    comparator = _comparator_from_r030(comparator_path)
    client = CachedTargetClient(NvidiaNIMProvider(), cache_dir)
    records: list[dict[str, Any]] = []
    calls = cache_hits = input_tokens = output_tokens = total_tokens = provider_failures = parse_failures = validation_failures = 0
    runtime_seconds = 0.0
    primitive_counts: Counter[str] = Counter()
    normalized_asts: set[str] = set()

    for tid in TASK_IDS:
        task = load_task(training_dir / f"{tid}.json", require_test_outputs=True)
        tests: list[dict[str, Any]] = []
        for i, pair in enumerate(task["test"]):
            tr: dict[str, Any] = {"test_index": i}
            try:
                req = TargetRequest(
                    model=MODEL,
                    prompt=candidate_prompt(task, pair["input"]),
                    solver_version=SOLVER_VERSION,
                    task_id=f"{tid}:test{i}",
                    attempt_index=0,
                    generation=GENERATION_CANDIDATES,
                )
                resp = client.generate(req)
                calls += 0 if resp.cache_hit else 1
                cache_hits += int(resp.cache_hit)
                input_tokens += resp.input_tokens or 0
                output_tokens += resp.output_tokens or 0
                total_tokens += resp.total_tokens or 0
                runtime_seconds += resp.runtime_seconds
                programs = parse_programs(resp.text)
                parse_failures += int(programs is None)
                tr["candidate_stage"] = {
                    "parsed": programs is not None,
                    "cache_hit": resp.cache_hit,
                    "input_tokens": resp.input_tokens,
                    "output_tokens": resp.output_tokens,
                    "total_tokens": resp.total_tokens,
                    "runtime_seconds": resp.runtime_seconds,
                    "finish_reason": (resp.provider_metadata or {}).get("finish_reason"),
                }
                if programs is None:
                    tests.append(tr)
                    continue
                for program in programs:
                    normalized_asts.add(json.dumps(program, sort_keys=True, separators=(",", ":")))
                    for step in program["steps"]:
                        primitive_counts[step["op"]] += 1
                try:
                    candidates = score_program_candidates(programs, pair["input"], pair["output"])
                except ValueError as exc:
                    validation_failures += 1
                    tr["validation_error"] = str(exc)[:200]
                    tests.append(tr)
                    continue
                tr["candidates"] = candidates
                tr["candidate_set_has_correct"] = any(c["candidate_correct"] for c in candidates)
            except Exception as exc:
                provider_failures += 1
                tr["error_type"] = type(exc).__name__
                tr["error"] = str(exc)[:200]
            tests.append(tr)
        records.append({"task_id": tid, "tests": tests})

    treatment = {
        r["task_id"]: bool(r["tests"]) and all(any(c.get("candidate_correct") is True for c in t.get("candidates", [])) for t in r["tests"])
        for r in records
    }
    delta = matched_coverage_delta(comparator, treatment)
    parseable_tasks = sum(all(t.get("candidate_stage", {}).get("parsed") is True for t in r["tests"]) for r in records)
    covered_tasks = sum(treatment.values())
    if provider_failures:
        verdict = "INCONCLUSIVE"
    elif parseable_tasks == 2 and covered_tasks >= 1:
        verdict = "PROMOTE"
    else:
        verdict = "REJECT"

    report = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "provider": PROVIDER,
        "model": MODEL,
        "solver_version": SOLVER_VERSION,
        "split": "dev_validation",
        "task_ids": TASK_IDS,
        "comparator_run": "ARC-R030",
        "candidate_generation": {
            "temperature": GENERATION_CANDIDATES.temperature,
            "top_p": GENERATION_CANDIDATES.top_p,
            "top_k": GENERATION_CANDIDATES.top_k,
            "max_output_tokens": GENERATION_CANDIDATES.max_output_tokens,
            "reasoning_effort": GENERATION_CANDIDATES.reasoning_effort,
        },
        "attempts_per_test": 1,
        "public_evaluation_used": False,
        "primary_change": "generic schema-v2 lattice-region peer map/reduce primitives; model/budget/scorer/task set otherwise frozen",
        "anti_overfit_constraints": [
            "no task IDs in primitive implementation or prompt hints",
            "no absolute task-specific coordinates",
            "no task-specific color constants",
            "no hand-entered target patterns",
        ],
        "comparator_coverage": comparator,
        "treatment_coverage": treatment,
        **delta,
        "parseable_tasks": parseable_tasks,
        "covered_tasks": covered_tasks,
        "calls": calls,
        "cache_hits": cache_hits,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "runtime_seconds": runtime_seconds,
        "provider_failures": provider_failures,
        "parse_failures": parse_failures,
        "program_validation_failures": validation_failures,
        "primitive_operator_counts": dict(sorted(primitive_counts.items())),
        "normalized_program_ast_count": len(normalized_asts),
        "records": records,
        "verdict": verdict,
        "adversarial_interpretation": (
            "A positive result would show only that this compact generic primitive family is sufficient on at least one diagnostic task under the matched prompt/model budget; "
            "it would not establish broad ARC generality. A 0/2 result after 2/2 parseability would shift the bottleneck toward induction/search or a different representation family rather than justify more token budget."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("training_dir", type=Path)
    p.add_argument("--comparator", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(run(a.training_dir, a.comparator, a.cache_dir, a.output), sort_keys=True))


if __name__ == "__main__":
    main()
