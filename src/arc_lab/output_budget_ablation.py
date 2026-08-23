from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from .baseline import build_prompt, parse_grid
from .splits import partition
from .target_model import CachedTargetClient, GenerationConfig, GoogleGenAIProvider, TargetRequest
from .taskio import load_task

EXPERIMENT_VERSION = "arc-r012-output-budget-ablation"
COMPARATOR_SOLVER_VERSION = "direct-json-v1-r011-response-diagnostic"
MODEL = "gemma-4-26b-a4b-it"
COMPARATOR_MAX_OUTPUT_TOKENS = 2048
TREATMENT_MAX_OUTPUT_TOKENS = 8192


def run_ablation(training_dir: Path, ids_file: Path, output: Path, cache_dir: Path) -> dict:
    ids = [line.strip() for line in ids_file.read_text().splitlines() if line.strip()]
    task_ids = partition(ids)["dev_validation"]
    task_id = task_ids[0]
    task = load_task(training_dir / f"{task_id}.json", require_test_outputs=True)
    test_index = 0
    prompt = build_prompt(task, task["test"][test_index]["input"])
    generation = GenerationConfig(
        temperature=1.0,
        top_p=0.95,
        top_k=64,
        max_output_tokens=TREATMENT_MAX_OUTPUT_TOKENS,
    )
    request = TargetRequest(
        model=MODEL,
        prompt=prompt,
        solver_version=COMPARATOR_SOLVER_VERSION,
        task_id=f"{task_id}:test{test_index}:r011-response-diagnostic",
        attempt_index=0,
        generation=generation,
    )
    response = CachedTargetClient(GoogleGenAIProvider(), cache_dir).generate(request)
    diagnostics = (response.provider_metadata or {}).get("response_diagnostics") or {}
    usage = diagnostics.get("usage") or {}
    candidates = diagnostics.get("candidates") or []
    finish_reasons = [candidate.get("finish_reason") for candidate in candidates]
    result = {
        "schema_version": 1,
        "experiment_version": EXPERIMENT_VERSION,
        "hypothesis": "Increasing only max_output_tokens from 2048 to 8192 on the exact ARC-R011 request allows Gemma to finish thinking and emit a non-empty final candidate.",
        "primary_variable": "max_output_tokens: 2048 -> 8192",
        "frozen": {
            "model": MODEL,
            "temperature": 1.0,
            "top_p": 0.95,
            "top_k": 64,
            "prompt": "identical by deterministic construction and checked against ARC-R011 prompt SHA",
            "split": "dev_validation",
            "task_id": task_id,
            "test_index": test_index,
            "attempt_index": 0,
            "solver_version": COMPARATOR_SOLVER_VERSION,
        },
        "comparator": {
            "max_output_tokens": COMPARATOR_MAX_OUTPUT_TOKENS,
            "input_tokens": 2982,
            "thought_tokens": 2045,
            "output_tokens": 0,
            "total_tokens": 5027,
            "runtime_seconds": 43.2723,
            "visible_text_chars": 0,
            "finish_reason": "MAX_TOKENS",
            "evidence": "lab/recon/gemma-empty-output-latest.json",
        },
        "model": MODEL,
        "split": "dev_validation",
        "task_id": task_id,
        "test_index": test_index,
        "attempt_index": 0,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "request_fingerprint": request.fingerprint(),
        "generation": asdict(generation),
        "cache_hit": response.cache_hit,
        "input_tokens": response.input_tokens,
        "thought_tokens": usage.get("thoughts_token_count"),
        "output_tokens": response.output_tokens,
        "total_tokens": response.total_tokens,
        "runtime_seconds": response.runtime_seconds,
        "visible_text": response.text,
        "visible_text_chars": len(response.text),
        "parsed_grid": parse_grid(response.text),
        "finish_reasons": finish_reasons,
        "provider_metadata": response.provider_metadata,
        "success": bool(response.text) and "MAX_TOKENS" not in finish_reasons,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "task_id": task_id,
        "cache_hit": response.cache_hit,
        "input_tokens": response.input_tokens,
        "thought_tokens": usage.get("thoughts_token_count"),
        "output_tokens": response.output_tokens,
        "total_tokens": response.total_tokens,
        "runtime_seconds": response.runtime_seconds,
        "visible_text_chars": len(response.text),
        "finish_reasons": finish_reasons,
        "parsed": result["parsed_grid"] is not None,
        "success": result["success"],
    }, sort_keys=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("training_dir", type=Path)
    parser.add_argument("ids_file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    args = parser.parse_args()
    run_ablation(args.training_dir, args.ids_file, args.output, args.cache_dir)


if __name__ == "__main__":
    main()
