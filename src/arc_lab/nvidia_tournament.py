from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .baseline import build_prompt, parse_grid
from .scoring import task_solved
from .splits import partition
from .target_model import CachedTargetClient, GenerationConfig, NvidiaNIMProvider, TargetRequest
from .taskio import load_task

MODELS = ("deepseek-ai/deepseek-v4-flash-0731", "nvidia/nemotron-3-ultra-550b-a55b")
SOLVER_VERSION = "nvidia-direct-json-tournament-v1"
GENERATION = GenerationConfig(temperature=0.0, top_p=1.0, top_k=None, max_output_tokens=4096)


def frozen_task_ids(ids_file: Path, count: int = 3) -> list[str]:
    ids = [x.strip() for x in ids_file.read_text().splitlines() if x.strip()]
    return partition(ids)["dev_validation"][:count]


def protocol_manifest(ids_file: Path, count: int = 3) -> dict[str, Any]:
    task_ids = frozen_task_ids(ids_file, count)
    payload = {
        "schema_version": 1, "run": "ARC-R015", "role": "llm-experimenter",
        "hypothesis": "Under identical direct-JSON decoding and one attempt per test input, one NVIDIA candidate will solve more tasks on the frozen slice; an exact-solve tie is inconclusive rather than broken by reputation.",
        "primary_variable": "target model identifier", "provider": "nvidia-nim",
        "models": list(MODELS), "split": "dev_validation", "selection_rule": "first 3 lexicographically sorted dev_validation IDs under arc-lab-v1",
        "task_ids": task_ids, "generation": asdict(GENERATION), "attempts_per_test": 1,
        "primary_metric": "exact full-task solves", "secondary": ["parseability", "tokens", "runtime", "provider failures"],
        "success_threshold": "strictly more exact full-task solves for one model", "falsification": "equal exact solves => INCONCLUSIVE",
        "public_evaluation_used": False,
        "exposure_note": "Foundation-model ARC-specific pretraining/exposure is not independently established by this run; scores are competition-utility evidence, not clean de-novo reasoning attribution."
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
    return payload


def run(training_dir: Path, ids_file: Path, cache_dir: Path, output: Path, count: int = 3) -> dict[str, Any]:
    manifest = protocol_manifest(ids_file, count)
    provider = NvidiaNIMProvider()
    results = []
    for model in MODELS:
        client = CachedTargetClient(provider, cache_dir / model.replace("/", "__"))
        solved = parse_failures = calls = cache_hits = input_tokens = output_tokens = total_tokens = failures = 0
        runtime = 0.0
        records = []
        for task_id in manifest["task_ids"]:
            task = load_task(training_dir / f"{task_id}.json", require_test_outputs=True)
            predictions, tests = [], []
            for test_index, pair in enumerate(task["test"]):
                request = TargetRequest(model=model, prompt=build_prompt(task, pair["input"]), solver_version=SOLVER_VERSION,
                    task_id=f"{task_id}:test{test_index}", attempt_index=0, generation=GENERATION)
                try:
                    response = client.generate(request)
                    grid = parse_grid(response.text)
                    parse_failures += int(grid is None)
                    predictions.append([] if grid is None else [grid])
                    calls += 0 if response.cache_hit else 1; cache_hits += int(response.cache_hit)
                    input_tokens += response.input_tokens or 0; output_tokens += response.output_tokens or 0; total_tokens += response.total_tokens or 0
                    runtime += response.runtime_seconds
                    tests.append({"test_index": test_index, "request_fingerprint": request.fingerprint(provider.provider_id), "cache_hit": response.cache_hit,
                        "model_resolved": response.model_resolved, "input_tokens": response.input_tokens, "output_tokens": response.output_tokens,
                        "total_tokens": response.total_tokens, "runtime_seconds": response.runtime_seconds, "parsed": grid is not None,
                        "finish_reason": (response.provider_metadata or {}).get("finish_reason"), "reasoning_chars": (response.provider_metadata or {}).get("reasoning_chars")})
                except Exception as exc:
                    failures += 1; predictions.append([]); tests.append({"test_index": test_index, "error_type": type(exc).__name__, "error": str(exc)[:300]})
            ok = len(predictions) == len(task["test"]) and all(predictions) and task_solved(predictions, [p["output"] for p in task["test"]])
            solved += int(ok); records.append({"task_id": task_id, "solved": ok, "tests": tests})
        results.append({"model": model, "solved_tasks": solved, "task_count": len(manifest["task_ids"]), "task_accuracy": solved / len(manifest["task_ids"]),
            "parse_failures": parse_failures, "provider_failures": failures, "calls": calls, "cache_hits": cache_hits,
            "input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": total_tokens, "runtime_seconds": runtime, "records": records})
    a, b = results
    if a["solved_tasks"] > b["solved_tasks"]: verdict, selected = "PROMOTE", a["model"]
    elif b["solved_tasks"] > a["solved_tasks"]: verdict, selected = "PROMOTE", b["model"]
    else: verdict, selected = "INCONCLUSIVE", None
    report = {"schema_version": 1, "manifest": manifest, "results": results, "verdict": verdict, "selected_primary": selected,
        "adversarial_interpretation": "A three-task slice has high variance; a win may reflect task-family fit or model pretraining exposure. Equal solves are not broken using parseability, latency, or reputation because exact solves are the declared primary metric."}
    output.parent.mkdir(parents=True, exist_ok=True); output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("training_dir", type=Path); p.add_argument("ids_file", type=Path); p.add_argument("--cache-dir", type=Path, required=True); p.add_argument("--output", type=Path, required=True); p.add_argument("--count", type=int, default=3)
    a = p.parse_args(); print(json.dumps(run(a.training_dir, a.ids_file, a.cache_dir, a.output, a.count), sort_keys=True))

if __name__ == "__main__": main()
