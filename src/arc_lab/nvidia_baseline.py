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

MODEL = "deepseek-ai/deepseek-v4-flash-0731"
PROVIDER = "nvidia-nim"
SOLVER_VERSION = "nvidia-direct-json-baseline-v1"
GENERATION = GenerationConfig(temperature=0.0, top_p=1.0, top_k=None, max_output_tokens=4096)
ATTEMPTS_PER_TEST = 1
CHUNK_COUNT = 6


def frozen_task_ids(ids_file: Path) -> list[str]:
    ids = [x.strip() for x in ids_file.read_text().splitlines() if x.strip()]
    return partition(ids)["dev_validation"]


def protocol_manifest(ids_file: Path) -> dict[str, Any]:
    task_ids = frozen_task_ids(ids_file)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "run": "ARC-R016",
        "role": "llm-experimenter",
        "hypothesis": "The ARC-R015-selected DeepSeek V4 Flash engine can establish a reproducible direct-JSON baseline across the entire frozen dev_validation split with exact task accounting and durable response-cache evidence.",
        "primary_variable": "none; baseline establishment under the ARC-R015-selected fixed model/protocol",
        "frozen_comparator": "ARC-R015 direct-JSON DeepSeek configuration",
        "provider": PROVIDER,
        "model": MODEL,
        "split": "dev_validation",
        "selection_rule": "all deterministic dev_validation IDs under arc-lab-v1",
        "task_ids": task_ids,
        "task_count": len(task_ids),
        "generation": asdict(GENERATION),
        "attempts_per_test": ATTEMPTS_PER_TEST,
        "provider_retry_policy": "no hidden retries; one provider request per uncached request fingerprint",
        "primary_metric": "exact full-task accuracy",
        "secondary": ["parseability", "tokens", "runtime", "provider failures", "cache hashes"],
        "success_threshold": "all frozen task IDs attempted with durable sanitized result/cache evidence",
        "falsification": "missing task IDs, duplicate task IDs, non-durable successful responses, or public-evaluation use => baseline not established",
        "public_evaluation_used": False,
        "exposure_note": "Foundation-model ARC-specific pretraining/exposure is not independently established by this run; score is competition-utility evidence, not clean de-novo reasoning attribution.",
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["manifest_sha256"] = hashlib.sha256(raw).hexdigest()
    return payload


def chunk_task_ids(task_ids: list[str], chunk_index: int, chunk_count: int = CHUNK_COUNT) -> list[str]:
    if chunk_count <= 0 or not 0 <= chunk_index < chunk_count:
        raise ValueError("invalid chunk index/count")
    return task_ids[chunk_index::chunk_count]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_chunk(
    training_dir: Path,
    ids_file: Path,
    cache_dir: Path,
    output: Path,
    *,
    chunk_index: int,
    chunk_count: int = CHUNK_COUNT,
) -> dict[str, Any]:
    manifest = protocol_manifest(ids_file)
    task_ids = chunk_task_ids(manifest["task_ids"], chunk_index, chunk_count)
    provider = NvidiaNIMProvider()
    client = CachedTargetClient(provider, cache_dir)

    solved = parse_failures = calls = cache_hits = input_tokens = output_tokens = total_tokens = provider_failures = 0
    runtime = 0.0
    records: list[dict[str, Any]] = []
    cache_records: list[dict[str, Any]] = []

    for task_id in task_ids:
        task = load_task(training_dir / f"{task_id}.json", require_test_outputs=True)
        predictions: list[list[list[list[int]]]] = []
        tests: list[dict[str, Any]] = []
        for test_index, pair in enumerate(task["test"]):
            request = TargetRequest(
                model=MODEL,
                prompt=build_prompt(task, pair["input"]),
                solver_version=SOLVER_VERSION,
                task_id=f"{task_id}:test{test_index}",
                attempt_index=0,
                generation=GENERATION,
            )
            fingerprint = request.fingerprint(provider.provider_id)
            cache_path = cache_dir / f"{fingerprint}.json"
            try:
                response = client.generate(request)
                grid = parse_grid(response.text)
                parse_failures += int(grid is None)
                predictions.append([] if grid is None else [grid])
                calls += 0 if response.cache_hit else 1
                cache_hits += int(response.cache_hit)
                input_tokens += response.input_tokens or 0
                output_tokens += response.output_tokens or 0
                total_tokens += response.total_tokens or 0
                runtime += response.runtime_seconds
                cache_sha = _sha256(cache_path) if cache_path.exists() else None
                if cache_sha:
                    cache_records.append({"request_fingerprint": fingerprint, "sha256": cache_sha, "file": cache_path.name})
                tests.append({
                    "test_index": test_index,
                    "request_fingerprint": fingerprint,
                    "cache_hit": response.cache_hit,
                    "cache_sha256": cache_sha,
                    "model_resolved": response.model_resolved,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "total_tokens": response.total_tokens,
                    "runtime_seconds": response.runtime_seconds,
                    "parsed_grid": grid,
                    "finish_reason": (response.provider_metadata or {}).get("finish_reason"),
                    "reasoning_chars": (response.provider_metadata or {}).get("reasoning_chars"),
                })
            except Exception as exc:
                provider_failures += 1
                predictions.append([])
                tests.append({
                    "test_index": test_index,
                    "request_fingerprint": fingerprint,
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:300],
                })
        expected = [p["output"] for p in task["test"]]
        is_solved = len(predictions) == len(expected) and all(predictions) and task_solved(predictions, expected)
        solved += int(is_solved)
        records.append({"task_id": task_id, "solved": is_solved, "tests": tests})

    report = {
        "schema_version": 1,
        "run": "ARC-R016",
        "manifest_sha256": manifest["manifest_sha256"],
        "provider": PROVIDER,
        "model": MODEL,
        "solver_version": SOLVER_VERSION,
        "generation": asdict(GENERATION),
        "attempts_per_test": ATTEMPTS_PER_TEST,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "task_ids": task_ids,
        "task_count": len(task_ids),
        "solved_tasks": solved,
        "task_accuracy": solved / len(task_ids) if task_ids else 0.0,
        "parse_failures": parse_failures,
        "provider_failures": provider_failures,
        "calls": calls,
        "cache_hits": cache_hits,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "runtime_seconds": runtime,
        "cache_records": cache_records,
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def aggregate(protocol_path: Path, chunks_dir: Path, output: Path, cache_manifest_output: Path) -> dict[str, Any]:
    protocol = json.loads(protocol_path.read_text())
    chunks = [json.loads(p.read_text()) for p in sorted(chunks_dir.glob("chunk-*.json"))]
    if len(chunks) != CHUNK_COUNT:
        raise ValueError(f"expected {CHUNK_COUNT} chunks, found {len(chunks)}")
    if any(c.get("manifest_sha256") != protocol.get("manifest_sha256") for c in chunks):
        raise ValueError("chunk/protocol manifest mismatch")

    records = [r for c in chunks for r in c["records"]]
    observed_ids = [r["task_id"] for r in records]
    expected_ids = protocol["task_ids"]
    if sorted(observed_ids) != sorted(expected_ids) or len(set(observed_ids)) != len(expected_ids):
        raise ValueError("aggregate task IDs do not exactly match frozen protocol")

    cache_records = [r for c in chunks for r in c["cache_records"]]
    successful_responses = sum(
        1 for r in records for t in r["tests"] if "error_type" not in t
    )
    if len(cache_records) != successful_responses:
        raise ValueError("every successful response must have durable cache hash evidence")

    solved = sum(int(r["solved"]) for r in records)
    totals = {
        key: sum(c[key] for c in chunks)
        for key in ("parse_failures", "provider_failures", "calls", "cache_hits", "input_tokens", "output_tokens", "total_tokens", "runtime_seconds")
    }
    failure_taxonomy = {
        "provider_failures": totals["provider_failures"],
        "parse_failures": totals["parse_failures"],
        "wrong_but_parseable_tasks": sum(1 for r in records if not r["solved"] and any(t.get("parsed_grid") is not None for t in r["tests"])),
        "solved_tasks": solved,
    }
    report = {
        "schema_version": 1,
        "run": "ARC-R016",
        "manifest": protocol,
        "provider": PROVIDER,
        "model": MODEL,
        "solver_version": SOLVER_VERSION,
        "task_count": len(expected_ids),
        "solved_tasks": solved,
        "task_accuracy": solved / len(expected_ids),
        **totals,
        "failure_taxonomy": failure_taxonomy,
        "records": sorted(records, key=lambda r: r["task_id"]),
        "verdict": "PROMOTE",
        "adversarial_interpretation": "This is a baseline measurement, not evidence that direct JSON is an optimal solver. Provider failures count as baseline failures. Known ARC-specific pretraining exposure was not independently established, so the score is competition-utility evidence rather than clean de-novo reasoning attribution.",
    }
    cache_manifest = {
        "schema_version": 1,
        "run": "ARC-R016",
        "manifest_sha256": protocol["manifest_sha256"],
        "successful_response_count": successful_responses,
        "cache_file_count": len(cache_records),
        "records": sorted(cache_records, key=lambda r: r["request_fingerprint"]),
        "note": "Cache JSON contains visible model output and sanitized provider metadata only; NVIDIA_API_KEY and reasoning text are not persisted.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    cache_manifest_output.write_text(json.dumps(cache_manifest, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run-chunk")
    r.add_argument("training_dir", type=Path)
    r.add_argument("ids_file", type=Path)
    r.add_argument("--cache-dir", type=Path, required=True)
    r.add_argument("--output", type=Path, required=True)
    r.add_argument("--chunk-index", type=int, required=True)
    r.add_argument("--chunk-count", type=int, default=CHUNK_COUNT)
    a = sub.add_parser("aggregate")
    a.add_argument("--protocol", type=Path, required=True)
    a.add_argument("--chunks-dir", type=Path, required=True)
    a.add_argument("--output", type=Path, required=True)
    a.add_argument("--cache-manifest-output", type=Path, required=True)
    args = p.parse_args()
    if args.command == "run-chunk":
        report = run_chunk(args.training_dir, args.ids_file, args.cache_dir, args.output, chunk_index=args.chunk_index, chunk_count=args.chunk_count)
    else:
        report = aggregate(args.protocol, args.chunks_dir, args.output, args.cache_manifest_output)
    print(json.dumps({k: report[k] for k in report if k in {"run", "task_count", "solved_tasks", "task_accuracy", "provider_failures", "parse_failures", "calls", "cache_hits", "total_tokens", "runtime_seconds", "verdict"}}, sort_keys=True))


if __name__ == "__main__":
    main()
