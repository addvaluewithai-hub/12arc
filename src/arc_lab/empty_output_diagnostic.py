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

DIAGNOSTIC_VERSION = "direct-json-v1-r011-response-diagnostic"
MODEL = "gemma-4-26b-a4b-it"


def run_diagnostic(training_dir: Path, ids_file: Path, output: Path, cache_dir: Path) -> dict:
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
        max_output_tokens=2048,
    )
    request = TargetRequest(
        model=MODEL,
        prompt=prompt,
        solver_version=DIAGNOSTIC_VERSION,
        task_id=f"{task_id}:test{test_index}:r011-response-diagnostic",
        attempt_index=0,
        generation=generation,
    )
    response = CachedTargetClient(GoogleGenAIProvider(), cache_dir).generate(request)
    result = {
        "schema_version": 1,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "hypothesis": "The frozen 2048-token generation budget is consumed by model thoughts before any visible candidate text is emitted.",
        "primary_variable": "response telemetry only; generation settings and prompt are unchanged from direct-json-v1",
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
        "output_tokens": response.output_tokens,
        "total_tokens": response.total_tokens,
        "runtime_seconds": response.runtime_seconds,
        "visible_text": response.text,
        "visible_text_chars": len(response.text),
        "parsed_grid": parse_grid(response.text),
        "provider_metadata": response.provider_metadata,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "task_id": task_id,
        "cache_hit": response.cache_hit,
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
        "total_tokens": response.total_tokens,
        "runtime_seconds": response.runtime_seconds,
        "visible_text_chars": len(response.text),
        "parsed": result["parsed_grid"] is not None,
    }, sort_keys=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("training_dir", type=Path)
    parser.add_argument("ids_file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    args = parser.parse_args()
    run_diagnostic(args.training_dir, args.ids_file, args.output, args.cache_dir)


if __name__ == "__main__":
    main()
