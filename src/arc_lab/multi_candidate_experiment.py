from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .multi_candidate import AccountingRecord, merge_accounting, verify_candidate_batch
from .target_model import CachedTargetClient, GenerationConfig, NvidiaNIMProvider, TargetRequest, TargetProviderError
from .taskio import load_task

MODEL = "deepseek-ai/deepseek-v4-flash-0731"
PROVIDER = "nvidia-nim"
GENERATION = GenerationConfig(temperature=0.7, top_p=0.95, top_k=64, max_output_tokens=4096)
CRITIQUE = GenerationConfig(temperature=0.2, top_p=0.95, top_k=64, max_output_tokens=3072)


def _json_slice(text: str, opening: str, closing: str) -> Any:
    start = text.find(opening)
    end = text.rfind(closing)
    if start < 0 or end < start:
        raise ValueError("response contains no parseable JSON container")
    return json.loads(text[start : end + 1])


def _call(client: CachedTargetClient, *, task_id: str, attempt: int, prompt: str, generation: GenerationConfig):
    request = TargetRequest(model=MODEL, prompt=prompt, solver_version="t0022-multi-candidate-v1", task_id=task_id, attempt_index=attempt, generation=generation)
    response = client.generate(request)
    accounting = AccountingRecord(
        request_count=0 if response.cache_hit else 1,
        cache_hits=1 if response.cache_hit else 0,
        input_tokens=response.input_tokens or 0,
        output_tokens=response.output_tokens or 0,
        total_tokens=response.total_tokens or ((response.input_tokens or 0) + (response.output_tokens or 0)),
        runtime_seconds=response.runtime_seconds,
    )
    return response, accounting


def run(task_path: Path, *, task_id: str, cache_dir: Path) -> dict[str, Any]:
    task = load_task(task_path, require_test_outputs=False)
    train_json = json.dumps(task["train"], separators=(",", ":"))
    client = CachedTargetClient(NvidiaNIMProvider(timeout_seconds=900), cache_dir, min_live_call_interval_seconds=1.0)
    accounts: list[AccountingRecord] = []
    raw_manifest: list[dict[str, Any]] = []

    generation_prompt = f"""You are an ARC candidate-program generator. Training pairs: {train_json}\nReturn ONLY a JSON array of exactly 16 DISTINCT candidate programs. Each program must use schema_version 1 or 2 supported by the supplied research DSL. Prefer diverse hypotheses: visual/global, object/region, lattice, exception/minimal decompositions. Do not include task IDs, absolute task-specific coordinates, known target patterns, prose, confidence scores, or final test answers. The deterministic Python executor will judge candidates."""
    response, account = _call(client, task_id=task_id, attempt=0, prompt=generation_prompt, generation=GENERATION)
    accounts.append(account)
    generated = _json_slice(response.text, "[", "]")
    if not isinstance(generated, list):
        raise ValueError("generator did not return a JSON list")
    raw_manifest.append({"phase": "generate", "cache_hit": response.cache_hit, "response_text": response.text})
    first_score = verify_candidate_batch(generated, task["train"])

    compact_scores = [{k: c[k] for k in ("candidate_id", "normalized_ir", "exact_training_pairs", "total_cell_error", "structural_violations")} for c in first_score["ranked_candidates"]]
    critique_prompt = f"""Act as a falsifying critic, not a judge. ARC training pairs: {train_json}\nCandidate Python metrics: {json.dumps(compact_scores, separators=(",", ":"))}\nReturn ONLY a JSON object with key critiques, a list of up to 8 objects containing candidate_id, likely_failure, violated_training_pair, forbidden_constant_risk, separator_or_unchanged_region_risk, and repair_suggestion. Use the Python metrics as evidence; do not claim correctness."""
    critique_response, account = _call(client, task_id=task_id, attempt=1, prompt=critique_prompt, generation=CRITIQUE)
    accounts.append(account)
    critiques = _json_slice(critique_response.text, "{", "}")
    raw_manifest.append({"phase": "critique", "cache_hit": critique_response.cache_hit, "response_text": critique_response.text})

    challenge_prompt = f"""Challenge these ARC candidate critiques for unsupported assumptions. Training pairs: {train_json}\nCritiques: {json.dumps(critiques, separators=(",", ":"))}\nReturn ONLY a JSON object with key challenges, listing candidate_id, critique_valid (boolean), reason, and smallest_general_repair. Do not choose a winner and do not invent execution results."""
    challenge_response, account = _call(client, task_id=task_id, attempt=2, prompt=challenge_prompt, generation=CRITIQUE)
    accounts.append(account)
    challenges = _json_slice(challenge_response.text, "{", "}")
    raw_manifest.append({"phase": "critique_the_critique", "cache_hit": challenge_response.cache_hit, "response_text": challenge_response.text})

    repair_prompt = f"""Repair ARC candidate programs using only general rules. Training pairs: {train_json}\nOriginal normalized candidates and metrics: {json.dumps(compact_scores, separators=(",", ":"))}\nCritiques: {json.dumps(critiques, separators=(",", ":"))}\nChallenges: {json.dumps(challenges, separators=(",", ":"))}\nReturn ONLY a JSON array of up to 8 repaired schema_version 1 or 2 programs. No prose, confidence, task IDs, absolute task-specific coordinates, or test answers."""
    repair_response, account = _call(client, task_id=task_id, attempt=3, prompt=repair_prompt, generation=GENERATION)
    accounts.append(account)
    repaired = _json_slice(repair_response.text, "[", "]")
    if not isinstance(repaired, list):
        raise ValueError("repairer did not return a JSON list")
    raw_manifest.append({"phase": "repair", "cache_hit": repair_response.cache_hit, "response_text": repair_response.text})

    final_score = verify_candidate_batch([*generated, *repaired], task["train"])
    return {
        "schema_version": 1,
        "task_id": task_id,
        "provider": PROVIDER,
        "model": MODEL,
        "generation_settings": {"generate_repair": asdict(GENERATION), "critique_challenge": asdict(CRITIQUE)},
        "attempts": 4,
        "raw_phase_manifest": raw_manifest,
        "critique_manifest": critiques,
        "critique_the_critique_manifest": challenges,
        "pre_repair_verification": first_score,
        "final_verification": final_score,
        "accounting": merge_accounting(accounts),
        "public_evaluation_used": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = run(args.task, task_id=args.task_id, cache_dir=args.cache_dir)
    except TargetProviderError as exc:
        result = {"schema_version": 1, "task_id": args.task_id, "status": "provider_failure", "provider_failure": {"message": str(exc), "status_code": exc.status_code, "retryable": exc.retryable, "rate_limit_headers": exc.rate_limit_headers}, "public_evaluation_used": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
