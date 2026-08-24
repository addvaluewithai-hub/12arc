from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .compact_hypothesis_search import (
    GENERATION_CANDIDATES,
    GENERATION_SELECTOR,
    MODEL,
    PROVIDER,
    SOLVER_VERSION,
    TASK_IDS,
    candidate_prompt,
    parse_hypotheses,
    parse_selector,
    selector_prompt,
)
from .target_model import CachedTargetClient, NvidiaNIMProvider, TargetRequest
from .taskio import load_task

RUN = "ARC-R020"


def _candidate_record(h: dict[str, Any], expected: list[list[int]]) -> dict[str, Any]:
    rule = h["rule"]
    grid = h["test_output"]
    return {
        "rule": rule,
        "rule_sha256": hashlib.sha256(rule.encode()).hexdigest(),
        "test_output": grid,
        "candidate_correct": grid == expected,
    }


def run(training_dir: Path, cache_dir: Path, output: Path) -> dict[str, Any]:
    client = CachedTargetClient(NvidiaNIMProvider(), cache_dir)
    records: list[dict[str, Any]] = []
    calls = cache_hits = input_tokens = output_tokens = total_tokens = provider_failures = 0
    runtime_seconds = 0.0

    for tid in TASK_IDS:
        task = load_task(training_dir / f"{tid}.json", require_test_outputs=True)
        tests: list[dict[str, Any]] = []
        for i, pair in enumerate(task["test"]):
            expected = pair["output"]
            tr: dict[str, Any] = {"test_index": i}
            try:
                creq = TargetRequest(model=MODEL, prompt=candidate_prompt(task, pair["input"]), solver_version=SOLVER_VERSION + ":candidates", task_id=f"{tid}:test{i}", attempt_index=0, generation=GENERATION_CANDIDATES)
                cresp = client.generate(creq)
                calls += 0 if cresp.cache_hit else 1
                cache_hits += int(cresp.cache_hit)
                input_tokens += cresp.input_tokens or 0
                output_tokens += cresp.output_tokens or 0
                total_tokens += cresp.total_tokens or 0
                runtime_seconds += cresp.runtime_seconds
                hypotheses = parse_hypotheses(cresp.text)
                tr["candidate_stage"] = {"parsed": hypotheses is not None, "cache_hit": cresp.cache_hit, "input_tokens": cresp.input_tokens, "output_tokens": cresp.output_tokens, "total_tokens": cresp.total_tokens, "runtime_seconds": cresp.runtime_seconds, "finish_reason": (cresp.provider_metadata or {}).get("finish_reason")}
                if hypotheses is None:
                    tests.append(tr)
                    continue
                candidates = [_candidate_record(h, expected) for h in hypotheses]
                tr["candidates"] = candidates
                tr["candidate_set_has_correct"] = any(c["candidate_correct"] for c in candidates)
                rules = [h["rule"] for h in hypotheses]
                sreq = TargetRequest(model=MODEL, prompt=selector_prompt(task, rules), solver_version=SOLVER_VERSION + ":selector", task_id=f"{tid}:test{i}", attempt_index=0, generation=GENERATION_SELECTOR)
                sresp = client.generate(sreq)
                calls += 0 if sresp.cache_hit else 1
                cache_hits += int(sresp.cache_hit)
                input_tokens += sresp.input_tokens or 0
                output_tokens += sresp.output_tokens or 0
                total_tokens += sresp.total_tokens or 0
                runtime_seconds += sresp.runtime_seconds
                selected = parse_selector(sresp.text)
                tr["selector_stage"] = {"parsed": selected is not None, "selected_index": selected, "cache_hit": sresp.cache_hit, "input_tokens": sresp.input_tokens, "output_tokens": sresp.output_tokens, "total_tokens": sresp.total_tokens, "runtime_seconds": sresp.runtime_seconds, "finish_reason": (sresp.provider_metadata or {}).get("finish_reason")}
                tr["selected_correct"] = None if selected is None else candidates[selected]["candidate_correct"]
            except Exception as exc:
                provider_failures += 1
                tr["error_type"] = type(exc).__name__
                tr["error"] = str(exc)[:200]
            tests.append(tr)
        records.append({"task_id": tid, "tests": tests})

    parseable = [r for r in records if all(t.get("candidate_stage", {}).get("parsed") for t in r["tests"])]
    covered = [r for r in parseable if all(t.get("candidate_set_has_correct", False) for t in r["tests"])]
    selected_correct = [r for r in parseable if all(t.get("selected_correct") is True for t in r["tests"])]
    prior_parseable_failures = {"00dbd492", "05f2a901", "070dd51e", "1190bc91"}
    diagnostic = [r for r in records if r["task_id"] in prior_parseable_failures and all(t.get("candidate_stage", {}).get("parsed") for t in r["tests"])]
    diagnostic_covered = [r for r in diagnostic if all(t.get("candidate_set_has_correct", False) for t in r["tests"])]
    coverage = len(diagnostic_covered) / len(diagnostic) if diagnostic else None
    if provider_failures:
        verdict = "INCONCLUSIVE"
        bottleneck = "provider failures confound diagnostic"
    elif len(diagnostic) < 4:
        verdict = "INCONCLUSIVE"
        bottleneck = "candidate parse failures prevent the predeclared four-task diagnostic"
    elif coverage is not None and coverage < 0.5:
        verdict = "INFRA_ONLY"
        bottleneck = "generator/representation"
    else:
        verdict = "INFRA_ONLY"
        bottleneck = "selector/ranking if covered candidates are not selected"

    report = {
        "schema_version": 1,
        "run": RUN,
        "role": "benchmark-methodologist",
        "primary_variable": "instrumentation only: persist and exact-score every generated candidate",
        "model_facing_protocol": "identical to ARC-R018 compact-hypothesis-select-v1",
        "provider": PROVIDER,
        "model": MODEL,
        "solver_version_for_requests": SOLVER_VERSION,
        "task_ids": TASK_IDS,
        "split": "dev_validation",
        "public_evaluation_used": False,
        "decision_boundary": "On the four prior parseable ARC-R018 failures, candidate-set coverage <50% => generator/representation bottleneck; >=50% with wrong selections => selector/ranking bottleneck.",
        "prior_parseable_failure_ids": sorted(prior_parseable_failures),
        "diagnostic_parseable_tasks": len(diagnostic),
        "diagnostic_candidate_covered_tasks": len(diagnostic_covered),
        "diagnostic_candidate_coverage": coverage,
        "all_parseable_tasks": len(parseable),
        "all_candidate_covered_tasks": len(covered),
        "all_selected_correct_tasks": len(selected_correct),
        "calls": calls,
        "cache_hits": cache_hits,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "runtime_seconds": runtime_seconds,
        "provider_failures": provider_failures,
        "bottleneck": bottleneck,
        "verdict": verdict,
        "records": records,
        "adversarial_interpretation": "A fresh deterministic-temperature rerun can still differ from ARC-R018 serving; this measures candidate coverage under the frozen protocol, not the unknowable historical unpersisted candidate set.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("training_dir", type=Path)
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    r = run(a.training_dir, a.cache_dir, a.output)
    print(json.dumps({k: r[k] for k in ["diagnostic_parseable_tasks", "diagnostic_candidate_covered_tasks", "diagnostic_candidate_coverage", "all_parseable_tasks", "all_candidate_covered_tasks", "all_selected_correct_tasks", "calls", "cache_hits", "total_tokens", "runtime_seconds", "provider_failures", "bottleneck", "verdict"]}, sort_keys=True))


if __name__ == "__main__":
    main()
