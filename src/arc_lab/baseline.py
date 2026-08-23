from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .scoring import task_solved
from .splits import partition
from .target_model import CachedTargetClient, GenerationConfig, GoogleGenAIProvider, TargetRequest
from .taskio import load_task, validate_grid

SOLVER_VERSION = "direct-json-v1"
GRID_RE = re.compile(r"\[\s*\[(?:.|\n)*?\]\s*\]")


def build_prompt(task: dict[str, Any], test_input: list[list[int]]) -> str:
    demos = [{"input": p["input"], "output": p["output"]} for p in task["train"]]
    return (
        "Solve this ARC grid transformation. Infer one rule from all training examples and apply it to the test input. "
        "Return ONLY the output grid as a JSON array of integer rows; no prose, markdown, or explanation.\n"
        + "TRAINING=" + json.dumps(demos, separators=(",", ":")) + "\n"
        + "TEST_INPUT=" + json.dumps(test_input, separators=(",", ":"))
    )


def parse_grid(text: str) -> list[list[int]] | None:
    candidates = [text.strip()]
    match = GRID_RE.search(text)
    if match:
        candidates.append(match.group(0))
    for candidate in candidates:
        try:
            value = json.loads(candidate)
            return validate_grid(value)
        except (ValueError, json.JSONDecodeError):
            pass
    return None


def run_baseline(training_dir: Path, ids_file: Path, output: Path, cache_dir: Path, *, split: str = "dev_validation") -> dict[str, Any]:
    ids = [line.strip() for line in ids_file.read_text().splitlines() if line.strip()]
    task_ids = partition(ids)[split]
    generation = GenerationConfig(temperature=1.0, top_p=0.95, top_k=64, max_output_tokens=2048)
    live_call_interval_seconds = float(
        os.environ.get("ARC_TARGET_MIN_LIVE_CALL_INTERVAL_SECONDS", "0")
    )
    client = CachedTargetClient(
        GoogleGenAIProvider(),
        cache_dir,
        min_live_call_interval_seconds=live_call_interval_seconds,
    )
    records = []
    calls = cache_hits = input_tokens = output_tokens = total_tokens = 0
    runtime = 0.0
    solved = 0
    parse_failures = 0

    for task_id in task_ids:
        task = load_task(training_dir / f"{task_id}.json", require_test_outputs=True)
        predictions_by_test = []
        test_records = []
        for test_index, pair in enumerate(task["test"]):
            attempts = []
            attempt_records = []
            for attempt_index in range(2):
                request = TargetRequest(
                    model="gemma-4-26b-a4b-it",
                    prompt=build_prompt(task, pair["input"]),
                    solver_version=SOLVER_VERSION,
                    task_id=f"{task_id}:test{test_index}",
                    attempt_index=attempt_index,
                    generation=generation,
                )
                response = client.generate(request)
                grid = parse_grid(response.text)
                if grid is not None:
                    attempts.append(grid)
                else:
                    parse_failures += 1
                calls += 0 if response.cache_hit else 1
                cache_hits += int(response.cache_hit)
                input_tokens += response.input_tokens or 0
                output_tokens += response.output_tokens or 0
                total_tokens += response.total_tokens or 0
                runtime += response.runtime_seconds
                attempt_records.append({
                    "attempt_index": attempt_index,
                    "request_fingerprint": request.fingerprint(),
                    "cache_hit": response.cache_hit,
                    "model_resolved": response.model_resolved,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "total_tokens": response.total_tokens,
                    "runtime_seconds": response.runtime_seconds,
                    "raw_text": response.text,
                    "parsed_grid": grid,
                })
            predictions_by_test.append(attempts)
            test_records.append({"test_index": test_index, "attempts": attempt_records})
        is_solved = len(predictions_by_test) == len(task["test"]) and all(predictions_by_test) and task_solved(predictions_by_test, [p["output"] for p in task["test"]])
        solved += int(is_solved)
        records.append({"task_id": task_id, "solved": is_solved, "tests": test_records})

    result = {
        "schema_version": 1,
        "solver_version": SOLVER_VERSION,
        "model": "gemma-4-26b-a4b-it",
        "split": split,
        "task_ids": task_ids,
        "task_count": len(task_ids),
        "generation": asdict(generation),
        "attempts_per_test": 2,
        "live_call_interval_seconds": live_call_interval_seconds,
        "solved_tasks": solved,
        "task_accuracy": solved / len(task_ids),
        "calls": calls,
        "cache_hits": cache_hits,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "runtime_seconds": runtime,
        "parse_failures": parse_failures,
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("training_dir", type=Path)
    parser.add_argument("ids_file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--split", default="dev_validation", choices=["dev_train", "dev_validation", "dev_holdout"])
    args = parser.parse_args()
    result = run_baseline(args.training_dir, args.ids_file, args.output, args.cache_dir, split=args.split)
    print(json.dumps({k: result[k] for k in ("split", "task_count", "solved_tasks", "task_accuracy", "calls", "cache_hits", "input_tokens", "output_tokens", "total_tokens", "runtime_seconds", "parse_failures", "live_call_interval_seconds")}, sort_keys=True))


if __name__ == "__main__":
    main()
