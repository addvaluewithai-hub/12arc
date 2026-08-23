from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .scoring import task_solved
from .target_model import CachedTargetClient, GenerationConfig, NvidiaNIMProvider, TargetRequest
from .taskio import load_task

MODEL = "deepseek-ai/deepseek-v4-flash-0731"
PROVIDER = "nvidia-nim"
SOLVER_VERSION = "compact-hypothesis-select-v1"
GENERATION_CANDIDATES = GenerationConfig(temperature=0.0, top_p=1.0, top_k=None, max_output_tokens=3072)
GENERATION_SELECTOR = GenerationConfig(temperature=0.0, top_p=1.0, top_k=None, max_output_tokens=512)
TASK_IDS = ["00dbd492", "05f2a901", "0607ce86", "06df4c85", "070dd51e", "0bb8deee", "0d3d703e", "1190bc91"]


def protocol_manifest() -> dict[str, Any]:
    p: dict[str, Any] = {
        "schema_version": 1,
        "run": "ARC-R018",
        "role": "reasoning-systems-inventor",
        "hypothesis": "Generating three compact competing rules and selecting among them using a separate training-only discriminator will improve exact accuracy over the frozen ARC-R016 direct-JSON comparator on the same eight deterministic dev_validation tasks, while avoiding ARC-R017 full-grid replay serialization failures.",
        "primary_variable": "two-stage compact multi-hypothesis generation plus training-only discriminative selection",
        "frozen_comparator": "ARC-R016 nvidia-direct-json-baseline-v1",
        "provider": PROVIDER,
        "model": MODEL,
        "solver_version": SOLVER_VERSION,
        "candidate_generation": asdict(GENERATION_CANDIDATES),
        "selector_generation": asdict(GENERATION_SELECTOR),
        "max_total_output_tokens_per_test": GENERATION_CANDIDATES.max_output_tokens + GENERATION_SELECTOR.max_output_tokens,
        "attempts_per_test": 1,
        "split": "dev_validation",
        "selection_rule": "same eight IDs used by ARC-R017",
        "task_ids": TASK_IDS,
        "primary_metric": "exact task accuracy versus ARC-R016 on identical IDs",
        "secondary": ["new solves", "regressions", "candidate parse failures", "selector parse failures", "provider failures", "tokens", "runtime"],
        "success_threshold": "PROMOTE only if treatment has at least one new solve and strictly more solved tasks than comparator",
        "falsification": "REJECT if treatment does not strictly beat comparator; INCONCLUSIVE only if provider failures prevent matched comparison",
        "public_evaluation_used": False,
        "exposure_note": "Known ARC-specific foundation-model exposure is not independently established; interpret as competition utility.",
    }
    raw = json.dumps(p, sort_keys=True, separators=(",", ":")).encode()
    p["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
    return p


def candidate_prompt(task: dict[str, Any], test_input: list[list[int]]) -> str:
    return (
        "Solve this ARC task by proposing exactly three DISTINCT compact transformation hypotheses. "
        "For each hypothesis return a short rule (max 240 characters) and the resulting test_output grid. "
        "Do not replay or serialize training outputs. Return JSON only with key hypotheses, where hypotheses is a list of exactly three objects with keys rule and test_output. No markdown.\n\n"
        "TRAINING:\n" + json.dumps(task["train"], separators=(",", ":")) +
        "\n\nTEST INPUT:\n" + json.dumps(test_input, separators=(",", ":"))
    )


def selector_prompt(task: dict[str, Any], rules: list[str]) -> str:
    return (
        "You are a discriminator, not a solver. Given ARC training pairs and three compact candidate rules, choose the ONE rule that best and most specifically explains every training transformation while making the fewest unsupported assumptions. "
        "You do not receive the test input or candidate test outputs. Return JSON only: {\"selected_index\":0|1|2,\"reason\":\"<=240 chars\"}. No markdown.\n\n"
        "TRAINING:\n" + json.dumps(task["train"], separators=(",", ":")) +
        "\n\nCANDIDATE RULES:\n" + json.dumps(rules, separators=(",", ":"))
    )


def _extract_json_object(text: str) -> dict[str, Any] | None:
    try:
        s = text.strip()
        start, end = s.find("{"), s.rfind("}")
        if start < 0 or end < start:
            return None
        value = json.loads(s[start:end + 1])
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def parse_hypotheses(text: str) -> list[dict[str, Any]] | None:
    obj = _extract_json_object(text)
    if obj is None:
        return None
    hypotheses = obj.get("hypotheses")
    if not isinstance(hypotheses, list) or len(hypotheses) != 3:
        return None
    clean: list[dict[str, Any]] = []
    for item in hypotheses:
        if not isinstance(item, dict):
            return None
        rule, grid = item.get("rule"), item.get("test_output")
        if not isinstance(rule, str) or not rule.strip() or len(rule) > 400 or not isinstance(grid, list):
            return None
        clean.append({"rule": rule.strip(), "test_output": grid})
    return clean


def parse_selector(text: str) -> int | None:
    obj = _extract_json_object(text)
    if obj is None:
        return None
    idx = obj.get("selected_index")
    return idx if isinstance(idx, int) and idx in (0, 1, 2) else None


def run(training_dir: Path, baseline_path: Path, cache_dir: Path, output: Path) -> dict[str, Any]:
    baseline = json.loads(baseline_path.read_text())
    base_by = {r["task_id"]: r for r in baseline["records"]}
    client = CachedTargetClient(NvidiaNIMProvider(), cache_dir)

    records: list[dict[str, Any]] = []
    calls = cache_hits = input_tokens = output_tokens = total_tokens = provider_failures = 0
    candidate_parse_failures = selector_parse_failures = 0
    runtime_seconds = 0.0

    for tid in TASK_IDS:
        task = load_task(training_dir / f"{tid}.json", require_test_outputs=True)
        predictions: list[list[list[list[int]]]] = []
        test_records: list[dict[str, Any]] = []

        for i, pair in enumerate(task["test"]):
            test_record: dict[str, Any] = {"test_index": i}
            try:
                candidate_req = TargetRequest(
                    model=MODEL,
                    prompt=candidate_prompt(task, pair["input"]),
                    solver_version=SOLVER_VERSION + ":candidates",
                    task_id=f"{tid}:test{i}",
                    attempt_index=0,
                    generation=GENERATION_CANDIDATES,
                )
                candidate_resp = client.generate(candidate_req)
                calls += 0 if candidate_resp.cache_hit else 1
                cache_hits += int(candidate_resp.cache_hit)
                input_tokens += candidate_resp.input_tokens or 0
                output_tokens += candidate_resp.output_tokens or 0
                total_tokens += candidate_resp.total_tokens or 0
                runtime_seconds += candidate_resp.runtime_seconds
                hypotheses = parse_hypotheses(candidate_resp.text)
                candidate_parse_failures += int(hypotheses is None)
                test_record["candidate_stage"] = {
                    "parsed": hypotheses is not None,
                    "cache_hit": candidate_resp.cache_hit,
                    "input_tokens": candidate_resp.input_tokens,
                    "output_tokens": candidate_resp.output_tokens,
                    "total_tokens": candidate_resp.total_tokens,
                    "runtime_seconds": candidate_resp.runtime_seconds,
                    "finish_reason": (candidate_resp.provider_metadata or {}).get("finish_reason"),
                }

                if hypotheses is None:
                    predictions.append([])
                    test_records.append(test_record)
                    continue

                rules = [h["rule"] for h in hypotheses]
                selector_req = TargetRequest(
                    model=MODEL,
                    prompt=selector_prompt(task, rules),
                    solver_version=SOLVER_VERSION + ":selector",
                    task_id=f"{tid}:test{i}",
                    attempt_index=0,
                    generation=GENERATION_SELECTOR,
                )
                selector_resp = client.generate(selector_req)
                calls += 0 if selector_resp.cache_hit else 1
                cache_hits += int(selector_resp.cache_hit)
                input_tokens += selector_resp.input_tokens or 0
                output_tokens += selector_resp.output_tokens or 0
                total_tokens += selector_resp.total_tokens or 0
                runtime_seconds += selector_resp.runtime_seconds
                selected = parse_selector(selector_resp.text)
                selector_parse_failures += int(selected is None)
                test_record["selector_stage"] = {
                    "parsed": selected is not None,
                    "selected_index": selected,
                    "cache_hit": selector_resp.cache_hit,
                    "input_tokens": selector_resp.input_tokens,
                    "output_tokens": selector_resp.output_tokens,
                    "total_tokens": selector_resp.total_tokens,
                    "runtime_seconds": selector_resp.runtime_seconds,
                    "finish_reason": (selector_resp.provider_metadata or {}).get("finish_reason"),
                }
                predictions.append([] if selected is None else [hypotheses[selected]["test_output"]])
                test_records.append(test_record)
            except Exception as exc:
                provider_failures += 1
                predictions.append([])
                test_record["error_type"] = type(exc).__name__
                test_record["error"] = str(exc)[:200]
                test_records.append(test_record)

        expected = [x["output"] for x in task["test"]]
        solved = len(predictions) == len(expected) and all(predictions) and task_solved(predictions, expected)
        baseline_solved = bool(base_by[tid]["solved"])
        records.append({
            "task_id": tid,
            "baseline_solved": baseline_solved,
            "treatment_solved": solved,
            "new_solve": solved and not baseline_solved,
            "regression": baseline_solved and not solved,
            "tests": test_records,
        })

    baseline_solved = sum(r["baseline_solved"] for r in records)
    treatment_solved = sum(r["treatment_solved"] for r in records)
    new_solves = sum(r["new_solve"] for r in records)
    regressions = sum(r["regression"] for r in records)
    verdict = "PROMOTE" if treatment_solved > baseline_solved and new_solves >= 1 else ("INCONCLUSIVE" if provider_failures else "REJECT")

    report = {
        "schema_version": 1,
        "run": "ARC-R018",
        "protocol": protocol_manifest(),
        "baseline_solved": baseline_solved,
        "treatment_solved": treatment_solved,
        "task_count": len(TASK_IDS),
        "baseline_accuracy": baseline_solved / len(TASK_IDS),
        "treatment_accuracy": treatment_solved / len(TASK_IDS),
        "new_solves": new_solves,
        "regressions": regressions,
        "candidate_parse_failures": candidate_parse_failures,
        "selector_parse_failures": selector_parse_failures,
        "provider_failures": provider_failures,
        "calls": calls,
        "cache_hits": cache_hits,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "runtime_seconds": runtime_seconds,
        "records": records,
        "verdict": verdict,
        "adversarial_interpretation": "The second stage may simply re-ask the same model to prefer its own wording, and repeating training pairs increases input cost. Eight tasks are directional, not a full-split estimate.",
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
    r = run(a.training_dir, a.baseline, a.cache_dir, a.output)
    print(json.dumps({k: r[k] for k in ["baseline_solved", "treatment_solved", "new_solves", "regressions", "candidate_parse_failures", "selector_parse_failures", "provider_failures", "calls", "total_tokens", "runtime_seconds", "verdict"]}, sort_keys=True))


if __name__ == "__main__":
    main()
