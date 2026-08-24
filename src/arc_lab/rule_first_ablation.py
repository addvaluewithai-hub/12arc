from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .compact_hypothesis_search import GENERATION_CANDIDATES, MODEL, PROVIDER
from .comparator_integrity import derive_task_candidate_coverage
from .rule_first import parse_program, score_program_candidates, matched_coverage_delta
from .target_model import CachedTargetClient, NvidiaNIMProvider, TargetRequest
from .taskio import load_task

TASK_IDS = ["0607ce86", "06df4c85"]
SOLVER_VERSION = "rule-first-overflow-v1"


def candidate_prompt(task: dict[str, Any], test_input: list[list[int]]) -> str:
    return (
        "Solve this ARC task by proposing exactly three DISTINCT compact programs. "
        "Do NOT serialize any output grid. Return JSON only with key programs, a list of exactly three objects. "
        "Each object must be a rule-first program with schema_version=1 and non-empty steps. "
        "Allowed ops: identity, rotate90, rotate180, rotate270, flip_h, flip_v, recolor. "
        "recolor step uses keys op, from, to with colors 0..9; all other ops have only key op. "
        "The programs will be executed deterministically on the test input after your response. No markdown.\n\n"
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
        return [parse_program(p) for p in programs]
    except Exception:
        return None


def run(training_dir: Path, baseline_path: Path, cache_dir: Path, output: Path) -> dict[str, Any]:
    baseline = json.loads(baseline_path.read_text())
    baseline_all = derive_task_candidate_coverage(baseline)
    comparator = {tid: baseline_all[tid] for tid in TASK_IDS}
    client = CachedTargetClient(NvidiaNIMProvider(), cache_dir)
    records: list[dict[str, Any]] = []
    calls = cache_hits = input_tokens = output_tokens = total_tokens = provider_failures = parse_failures = validation_failures = 0
    runtime_seconds = 0.0

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
                try:
                    candidates = score_program_candidates(programs, pair["input"], pair["output"])
                except ValueError:
                    validation_failures += 1
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

    treatment = derive_task_candidate_coverage({"records": records})
    delta = matched_coverage_delta(comparator, treatment)
    parseable_tasks = sum(all(t.get("candidate_stage", {}).get("parsed") is True for t in r["tests"]) for r in records)
    covered_tasks = sum(treatment.values())
    verdict = "PROMOTE" if parseable_tasks == 2 and covered_tasks >= 1 and not provider_failures else ("INCONCLUSIVE" if provider_failures else "REJECT")
    report = {
        "schema_version": 1,
        "task_id": "T0015-RULE-FIRST-OVERFLOW-ABLATION",
        "provider": PROVIDER,
        "model": MODEL,
        "solver_version": SOLVER_VERSION,
        "split": "dev_validation",
        "task_ids": TASK_IDS,
        "candidate_generation": {
            "temperature": GENERATION_CANDIDATES.temperature,
            "top_p": GENERATION_CANDIDATES.top_p,
            "top_k": GENERATION_CANDIDATES.top_k,
            "max_output_tokens": GENERATION_CANDIDATES.max_output_tokens,
            "reasoning_effort": GENERATION_CANDIDATES.reasoning_effort,
        },
        "attempts_per_test": 1,
        "public_evaluation_used": False,
        "primary_change": "candidate response serialization only: compact executable programs instead of materialized grids",
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
        "records": records,
        "verdict": verdict,
        "adversarial_interpretation": "A compact syntax can remove serialization overflow while still failing because the bounded generic IR lacks the semantic primitive needed by a task; parseability alone is not evidence of reasoning improvement.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("training_dir", type=Path)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(run(a.training_dir, a.baseline, a.cache_dir, a.output), sort_keys=True))


if __name__ == "__main__":
    main()
