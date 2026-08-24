from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from .baseline import build_prompt, parse_grid
from .scoring import task_solved
from .splits import partition
from .target_model import (
    CachedTargetClient,
    GenerationConfig,
    NvidiaNIMProvider,
    TargetProviderError,
    TargetRequest,
)
from .taskio import load_task

MODEL = "deepseek-ai/deepseek-v4-flash-0731"
PROVIDER = "nvidia-nim"
SOLVER_VERSION = "nvidia-direct-json-max-reasoning-v1"
TASK_ID = "T0012-MAX-REASONING-DIRECT-ABLATION"
GENERATION = GenerationConfig(
    temperature=0.0,
    top_p=1.0,
    top_k=None,
    max_output_tokens=16384,
    reasoning_effort="max",
)
PROVIDER_TIMEOUT_SECONDS = 900.0
MAX_TRANSPORT_RETRIES = 2
SOURCE_COMMIT = "f3283f727488ad98fe575ea6a5ac981e4a188e49"
RUN_RE = re.compile(r"^ARC-R\d{3,}$")


def frozen_task_ids(ids_file: Path) -> list[str]:
    ids = [x.strip() for x in ids_file.read_text().splitlines() if x.strip()]
    return partition(ids)["dev_validation"]


def _sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_trigger(
    trigger_path: Path,
    queue_path: Path,
    run_counter_path: Path,
) -> dict[str, Any]:
    trigger = json.loads(trigger_path.read_text())
    if trigger.get("schema_version") != 1:
        raise ValueError("trigger schema_version must be 1")
    if trigger.get("task_id") != TASK_ID:
        raise ValueError(f"trigger task_id must be {TASK_ID}")
    run = trigger.get("run")
    shift_id = trigger.get("shift_id")
    if not isinstance(run, str) or not RUN_RE.fullmatch(run):
        raise ValueError("trigger run must look like ARC-RNNN")
    if not isinstance(shift_id, str) or not shift_id:
        raise ValueError("trigger shift_id is required")

    queue = json.loads(queue_path.read_text())
    task = next((t for t in queue.get("tasks", []) if t.get("id") == TASK_ID), None)
    if task is None or task.get("status") != "claimed":
        raise ValueError("T0012 must be claimed before its trigger is written")
    claim = task.get("claim") or {}
    if claim.get("shift_id") != shift_id:
        raise ValueError("trigger shift_id does not match the active T0012 claim")

    counter = json.loads(run_counter_path.read_text())
    reservation = next(
        (
            r
            for r in counter.get("active_reservations", [])
            if r.get("run") == run
            and r.get("task_id") == TASK_ID
            and r.get("shift_id") == shift_id
        ),
        None,
    )
    if reservation is None:
        raise ValueError("trigger does not match an active T0012 run reservation")
    return trigger


def protocol_manifest(
    planned_protocol_path: Path,
    ids_file: Path,
    trigger: dict[str, Any],
) -> dict[str, Any]:
    planned = json.loads(planned_protocol_path.read_text())
    if planned.get("task_id") != TASK_ID:
        raise ValueError("planned protocol task_id mismatch")
    task_ids = frozen_task_ids(ids_file)
    if planned.get("task_count") != len(task_ids):
        raise ValueError("planned task_count does not match deterministic dev_validation")
    payload = {
        **planned,
        "status": "frozen",
        "run": trigger["run"],
        "source_commit": SOURCE_COMMIT,
        "task_ids": task_ids,
        "task_ids_sha256": _sha256_json(task_ids),
        "trigger": {
            "task_id": trigger["task_id"],
            "run": trigger["run"],
            "shift_id": trigger["shift_id"],
            "requested_at": trigger.get("requested_at"),
        },
    }
    payload.pop("manifest_sha256", None)
    payload["manifest_sha256"] = _sha256_json(payload)
    return payload


def output_token_bucket(output_tokens: int | None) -> str:
    if output_tokens is None:
        return "unknown"
    if output_tokens >= 16384:
        return "16384_cap"
    if output_tokens <= 4096:
        return "<=4096"
    if output_tokens <= 8192:
        return "4097-8192"
    return "8193-16383"


def _retry_delay_seconds(error: TargetProviderError, retry_index: int) -> float:
    value = error.rate_limit_headers.get("retry-after")
    if value is not None:
        try:
            return max(0.0, float(value))
        except ValueError:
            pass
    return (5.0, 15.0)[min(retry_index, 1)]


def _response_record(
    response: Any,
    *,
    transport_attempt: int,
    fingerprint: str,
    grid: list[list[int]] | None,
) -> dict[str, Any]:
    metadata = response.provider_metadata or {}
    return {
        "transport_attempt": transport_attempt,
        "request_fingerprint": fingerprint,
        "ok": True,
        "cache_hit": response.cache_hit,
        "model_resolved": response.model_resolved,
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
        "total_tokens": response.total_tokens,
        "runtime_seconds": response.runtime_seconds,
        "finish_reason": metadata.get("finish_reason"),
        "reasoning_chars": metadata.get("reasoning_chars"),
        "rate_limit_headers": metadata.get("rate_limit_headers") or {},
        "output_token_bucket": output_token_bucket(response.output_tokens),
        "parsed_grid": grid,
    }


def _error_record(
    error: Exception,
    *,
    transport_attempt: int,
    fingerprint: str,
) -> dict[str, Any]:
    if isinstance(error, TargetProviderError):
        return {
            "transport_attempt": transport_attempt,
            "request_fingerprint": fingerprint,
            "ok": False,
            "error_type": type(error).__name__,
            "error": str(error)[:500],
            "status_code": error.status_code,
            "retryable": error.retryable,
            "rate_limit_headers": error.rate_limit_headers,
        }
    return {
        "transport_attempt": transport_attempt,
        "request_fingerprint": fingerprint,
        "ok": False,
        "error_type": type(error).__name__,
        "error": str(error)[:500],
        "status_code": None,
        "retryable": False,
        "rate_limit_headers": {},
    }


def run_task(
    training_dir: Path,
    task_id: str,
    cache_dir: Path,
    output: Path,
    *,
    provider_timeout_seconds: float = PROVIDER_TIMEOUT_SECONDS,
    max_transport_retries: int = MAX_TRANSPORT_RETRIES,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    if max_transport_retries < 0:
        raise ValueError("max_transport_retries must be non-negative")
    resume_path = cache_dir / "task-result.json"
    if resume_path.exists():
        report = json.loads(resume_path.read_text())
        if report.get("task_id") != task_id or report.get("solver_version") != SOLVER_VERSION:
            raise ValueError("cached task-result identity mismatch")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return report

    task = load_task(training_dir / f"{task_id}.json", require_test_outputs=True)
    provider = NvidiaNIMProvider(timeout_seconds=provider_timeout_seconds)
    client = CachedTargetClient(provider, cache_dir)

    first_attempt_predictions: list[list[list[list[int]]]] = []
    recovered_predictions: list[list[list[list[int]]]] = []
    test_records: list[dict[str, Any]] = []
    live_calls = cache_hits = input_tokens = output_tokens = total_tokens = 0
    runtime_seconds = 0.0
    parse_failures = terminal_provider_failures = transport_failure_events = 0

    for test_index, pair in enumerate(task["test"]):
        attempts: list[dict[str, Any]] = []
        final_grid: list[list[int]] | None = None
        success_transport_attempt: int | None = None

        for transport_attempt in range(max_transport_retries + 1):
            request = TargetRequest(
                model=MODEL,
                prompt=build_prompt(task, pair["input"]),
                solver_version=SOLVER_VERSION,
                task_id=f"{task_id}:test{test_index}",
                attempt_index=transport_attempt,
                generation=GENERATION,
            )
            fingerprint = request.fingerprint(provider.provider_id)
            try:
                response = client.generate(request)
                grid = parse_grid(response.text)
                attempts.append(
                    _response_record(
                        response,
                        transport_attempt=transport_attempt,
                        fingerprint=fingerprint,
                        grid=grid,
                    )
                )
                live_calls += 0 if response.cache_hit else 1
                cache_hits += int(response.cache_hit)
                input_tokens += response.input_tokens or 0
                output_tokens += response.output_tokens or 0
                total_tokens += response.total_tokens or 0
                runtime_seconds += response.runtime_seconds
                parse_failures += int(grid is None)
                final_grid = grid
                success_transport_attempt = transport_attempt
                break
            except Exception as exc:
                record = _error_record(
                    exc,
                    transport_attempt=transport_attempt,
                    fingerprint=fingerprint,
                )
                attempts.append(record)
                live_calls += 1
                transport_failure_events += 1
                retryable = isinstance(exc, TargetProviderError) and exc.retryable
                if retryable and transport_attempt < max_transport_retries:
                    sleep(_retry_delay_seconds(exc, transport_attempt))
                    continue
                terminal_provider_failures += 1
                break

        if final_grid is None:
            first_attempt_predictions.append([])
            recovered_predictions.append([])
        else:
            recovered_predictions.append([final_grid])
            first_attempt_predictions.append(
                [final_grid] if success_transport_attempt == 0 else []
            )
        test_records.append(
            {
                "test_index": test_index,
                "success_transport_attempt": success_transport_attempt,
                "attempts": attempts,
            }
        )

    expected = [p["output"] for p in task["test"]]
    first_attempt_solved = (
        len(first_attempt_predictions) == len(expected)
        and all(first_attempt_predictions)
        and task_solved(first_attempt_predictions, expected)
    )
    recovered_solved = (
        len(recovered_predictions) == len(expected)
        and all(recovered_predictions)
        and task_solved(recovered_predictions, expected)
    )
    report = {
        "schema_version": 1,
        "task_id": task_id,
        "provider": PROVIDER,
        "model": MODEL,
        "solver_version": SOLVER_VERSION,
        "generation": asdict(GENERATION),
        "provider_timeout_seconds": provider_timeout_seconds,
        "max_transport_retries": max_transport_retries,
        "first_attempt_solved": first_attempt_solved,
        "operational_recovered_solved": recovered_solved,
        "required_transport_recovery": any(
            t["success_transport_attempt"] not in {None, 0} for t in test_records
        ),
        "live_calls": live_calls,
        "cache_hits": cache_hits,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "runtime_seconds": runtime_seconds,
        "parse_failures": parse_failures,
        "terminal_provider_failures": terminal_provider_failures,
        "transport_failure_events": transport_failure_events,
        "tests": test_records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    output.write_text(serialized)
    resume_path.write_text(serialized)
    return report


def aggregate(
    protocol_path: Path,
    parts_dir: Path,
    comparator_path: Path,
    output: Path,
) -> dict[str, Any]:
    protocol = json.loads(protocol_path.read_text())
    expected_ids = protocol["task_ids"]
    parts = [json.loads(p.read_text()) for p in sorted(parts_dir.glob("task-*.json"))]
    observed_ids = [p.get("task_id") for p in parts]
    if sorted(observed_ids) != sorted(expected_ids) or len(set(observed_ids)) != len(expected_ids):
        raise ValueError("task artifacts do not exactly match frozen protocol task IDs")

    comparator = json.loads(comparator_path.read_text())
    comparator_records = comparator.get("records") or []
    comparator_map = {r["task_id"]: bool(r["solved"]) for r in comparator_records}
    if set(comparator_map) != set(expected_ids):
        raise ValueError("comparator task set does not exactly match frozen protocol")

    first_map = {p["task_id"]: bool(p["first_attempt_solved"]) for p in parts}
    recovered_map = {
        p["task_id"]: bool(p["operational_recovered_solved"]) for p in parts
    }
    new_solves = sorted(k for k in expected_ids if first_map[k] and not comparator_map[k])
    regressions = sorted(k for k in expected_ids if comparator_map[k] and not first_map[k])
    recovered_new_solves = sorted(
        k for k in expected_ids if recovered_map[k] and not comparator_map[k]
    )
    recovered_regressions = sorted(
        k for k in expected_ids if comparator_map[k] and not recovered_map[k]
    )

    buckets = {"<=4096": 0, "4097-8192": 0, "8193-16383": 0, "16384_cap": 0, "unknown": 0}
    finish_reasons: dict[str, int] = {}
    rate_limit_snapshots: list[dict[str, Any]] = []
    for part in parts:
        for test in part.get("tests", []):
            for attempt in test.get("attempts", []):
                headers = attempt.get("rate_limit_headers") or {}
                if headers:
                    rate_limit_snapshots.append(
                        {
                            "task_id": part["task_id"],
                            "test_index": test["test_index"],
                            "transport_attempt": attempt["transport_attempt"],
                            "headers": headers,
                        }
                    )
                if not attempt.get("ok"):
                    continue
                bucket = attempt.get("output_token_bucket", "unknown")
                buckets[bucket] = buckets.get(bucket, 0) + 1
                reason = str(attempt.get("finish_reason") or "unknown")
                finish_reasons[reason] = finish_reasons.get(reason, 0) + 1

    first_solved = sum(first_map.values())
    recovered_solved = sum(recovered_map.values())
    baseline_solved = sum(comparator_map.values())
    totals = {
        key: sum(p.get(key, 0) or 0 for p in parts)
        for key in (
            "live_calls",
            "cache_hits",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "runtime_seconds",
            "parse_failures",
            "terminal_provider_failures",
            "transport_failure_events",
        )
    }
    report = {
        "schema_version": 1,
        "run": protocol["run"],
        "task_id": TASK_ID,
        "manifest_sha256": protocol["manifest_sha256"],
        "provider": PROVIDER,
        "model": MODEL,
        "solver_version": SOLVER_VERSION,
        "generation": asdict(GENERATION),
        "task_count": len(expected_ids),
        "comparator": {
            "run": comparator.get("run", "ARC-R016"),
            "solved": baseline_solved,
            "accuracy": baseline_solved / len(expected_ids),
        },
        "primary_first_attempt": {
            "solved": first_solved,
            "accuracy": first_solved / len(expected_ids),
            "new_solves": new_solves,
            "regressions": regressions,
        },
        "operational_with_transport_recovery": {
            "solved": recovered_solved,
            "accuracy": recovered_solved / len(expected_ids),
            "new_solves": recovered_new_solves,
            "regressions": recovered_regressions,
        },
        **totals,
        "finish_reason_distribution": dict(sorted(finish_reasons.items())),
        "output_token_length_buckets": buckets,
        "rate_limit_snapshots": rate_limit_snapshots,
        "records": sorted(parts, key=lambda p: p["task_id"]),
        "public_evaluation_used": False,
        "verdict": "PROMOTE" if first_solved > baseline_solved else "REJECT",
        "causal_limit": "reasoning_effort=max and max_output_tokens=16384 changed together; this measures maximum supported direct-inference utility, not separate causality.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def _prepare_command(args: argparse.Namespace) -> dict[str, Any]:
    trigger = validate_trigger(args.trigger, args.queue, args.run_counter)
    protocol = protocol_manifest(args.planned_protocol, args.ids_file, trigger)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(protocol, indent=2, sort_keys=True) + "\n")
    return {
        "run": protocol["run"],
        "task_ids": protocol["task_ids"],
        "manifest_sha256": protocol["manifest_sha256"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("prepare")
    p.add_argument("--planned-protocol", type=Path, required=True)
    p.add_argument("--ids-file", type=Path, required=True)
    p.add_argument("--trigger", type=Path, required=True)
    p.add_argument("--queue", type=Path, required=True)
    p.add_argument("--run-counter", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)

    r = sub.add_parser("run-task")
    r.add_argument("training_dir", type=Path)
    r.add_argument("--task-id", required=True)
    r.add_argument("--cache-dir", type=Path, required=True)
    r.add_argument("--output", type=Path, required=True)
    r.add_argument("--provider-timeout-seconds", type=float, default=PROVIDER_TIMEOUT_SECONDS)
    r.add_argument("--max-transport-retries", type=int, default=MAX_TRANSPORT_RETRIES)

    a = sub.add_parser("aggregate")
    a.add_argument("--protocol", type=Path, required=True)
    a.add_argument("--parts-dir", type=Path, required=True)
    a.add_argument("--comparator", type=Path, required=True)
    a.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "prepare":
        summary = _prepare_command(args)
    elif args.command == "run-task":
        report = run_task(
            args.training_dir,
            args.task_id,
            args.cache_dir,
            args.output,
            provider_timeout_seconds=args.provider_timeout_seconds,
            max_transport_retries=args.max_transport_retries,
        )
        summary = {
            key: report[key]
            for key in (
                "task_id",
                "first_attempt_solved",
                "operational_recovered_solved",
                "live_calls",
                "total_tokens",
                "terminal_provider_failures",
            )
        }
    else:
        report = aggregate(args.protocol, args.parts_dir, args.comparator, args.output)
        summary = {
            "run": report["run"],
            "task_count": report["task_count"],
            "primary_first_attempt": report["primary_first_attempt"],
            "operational_with_transport_recovery": report[
                "operational_with_transport_recovery"
            ],
            "live_calls": report["live_calls"],
            "total_tokens": report["total_tokens"],
            "verdict": report["verdict"],
        }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
