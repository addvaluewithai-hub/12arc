from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .multi_candidate import AccountingRecord, merge_accounting, verify_candidate_batch
from .multi_candidate_contract import prompt_contract_fragment, validate_candidate_contract
from .target_model import CachedTargetClient, GenerationConfig, NvidiaNIMProvider, TargetRequest, TargetProviderError
from .taskio import load_task

DEFAULT_MODEL = "deepseek-ai/deepseek-v4-flash-0731"
MODEL = os.environ.get("ARC_TARGET_MODEL", DEFAULT_MODEL)
PROVIDER = "nvidia-nim"
GENERATION = GenerationConfig(temperature=0.7, top_p=0.95, top_k=64, max_output_tokens=4096)
CRITIQUE = GenerationConfig(temperature=0.2, top_p=0.95, top_k=64, max_output_tokens=3072)


def _json_slice(text: str, opening: str, closing: str) -> Any:
    """Return the first valid JSON container of the requested kind.

    Hosted models often wrap JSON in prose or markdown. The verifier must still
    fail closed, but it should not crash before persisting the raw response.
    """

    expected_type = list if opening == "[" else dict
    decoder = json.JSONDecoder()
    for start, char in enumerate(text):
        if char != opening:
            continue
        try:
            value, _end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, expected_type):
            return value
    preview = text[:500].replace("\n", "\\n")
    raise ValueError(
        f"response contains no parseable JSON {opening}{closing} container; preview={preview!r}"
    )


def _call(client: CachedTargetClient, *, task_id: str, attempt: int, prompt: str, generation: GenerationConfig):
    request = TargetRequest(model=MODEL, prompt=prompt, solver_version="t0022-multi-candidate-v2-contract", task_id=task_id, attempt_index=attempt, generation=generation)
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


def _operational_failure(
    *,
    task_id: str,
    stage: str,
    exc: Exception,
    accounts: list[AccountingRecord],
    raw_manifest: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "task_id": task_id,
        "status": "operational_failure",
        "provider": PROVIDER,
        "model": MODEL,
        "default_model": DEFAULT_MODEL,
        "model_override_used": MODEL != DEFAULT_MODEL,
        "solver_version": "t0022-multi-candidate-v2-contract",
        "failure_stage": stage,
        "error_type": type(exc).__name__,
        "error_message": str(exc)[:1000],
        "raw_phase_manifest": raw_manifest,
        "accounting": merge_accounting(accounts),
        "public_evaluation_used": False,
    }


def run(task_path: Path, *, task_id: str, cache_dir: Path) -> dict[str, Any]:
    task = load_task(task_path, require_test_outputs=False)
    train_json = json.dumps(task["train"], separators=(",", ":"))
    contract = prompt_contract_fragment()
    client = CachedTargetClient(NvidiaNIMProvider(timeout_seconds=900), cache_dir, min_live_call_interval_seconds=1.0)
    accounts: list[AccountingRecord] = []
    raw_manifest: list[dict[str, Any]] = []
    stage = "initialize"

    try:
        generation_prompt = f"""You are an ARC candidate-program generator. Training pairs: {train_json}\n{contract}\nReturn ONLY a JSON array of exactly 16 DISTINCT executable candidate objects satisfying that contract. Prefer diverse hypotheses expressible by the allowed operators. Do not include task IDs, absolute task-specific coordinates, known target patterns, prose, confidence scores, or final test answers. The deterministic Python executor will judge candidates. The first character of your response must be [ and the last character must be ]."""
        stage = "generate_call"
        response, account = _call(client, task_id=task_id, attempt=0, prompt=generation_prompt, generation=GENERATION)
        accounts.append(account)
        raw_manifest.append({"phase": "generate", "cache_hit": response.cache_hit, "response_text": response.text})
        stage = "generate_parse"
        generated = _json_slice(response.text, "[", "]")
        if not isinstance(generated, list):
            raise ValueError("generator did not return a JSON list")
        stage = "generate_contract"
        generation_contract = validate_candidate_contract(generated)
        stage = "generate_verify"
        first_score = verify_candidate_batch(generated, task["train"])

        compact_scores = [{k: c[k] for k in ("candidate_id", "normalized_ir", "exact_training_pairs", "total_cell_error", "structural_violations")} for c in first_score["ranked_candidates"]]
        critique_prompt = f"""Act as a falsifying critic, not a judge. ARC training pairs: {train_json}\nCandidate Python metrics: {json.dumps(compact_scores, separators=(",", ":"))}\nReturn ONLY a JSON object with key critiques, a list of up to 8 objects containing candidate_id, likely_failure, violated_training_pair, forbidden_constant_risk, separator_or_unchanged_region_risk, and repair_suggestion. Use the Python metrics as evidence; do not claim correctness. The first character of your response must be {{ and the last character must be }}."""
        stage = "critique_call"
        critique_response, account = _call(client, task_id=task_id, attempt=1, prompt=critique_prompt, generation=CRITIQUE)
        accounts.append(account)
        raw_manifest.append({"phase": "critique", "cache_hit": critique_response.cache_hit, "response_text": critique_response.text})
        stage = "critique_parse"
        critiques = _json_slice(critique_response.text, "{", "}")

        challenge_prompt = f"""Challenge these ARC candidate critiques for unsupported assumptions. Training pairs: {train_json}\nCritiques: {json.dumps(critiques, separators=(",", ":"))}\nReturn ONLY a JSON object with key challenges, listing candidate_id, critique_valid (boolean), reason, and smallest_general_repair. Do not choose a winner and do not invent execution results. The first character of your response must be {{ and the last character must be }}."""
        stage = "critique_the_critique_call"
        challenge_response, account = _call(client, task_id=task_id, attempt=2, prompt=challenge_prompt, generation=CRITIQUE)
        accounts.append(account)
        raw_manifest.append({"phase": "critique_the_critique", "cache_hit": challenge_response.cache_hit, "response_text": challenge_response.text})
        stage = "critique_the_critique_parse"
        challenges = _json_slice(challenge_response.text, "{", "}")

        repair_prompt = f"""Repair ARC candidate programs using only general rules. Training pairs: {train_json}\nOriginal normalized candidates and metrics: {json.dumps(compact_scores, separators=(",", ":"))}\nCritiques: {json.dumps(critiques, separators=(",", ":"))}\nChallenges: {json.dumps(challenges, separators=(",", ":"))}\n{contract}\nReturn ONLY a JSON array of up to 8 repaired executable candidate objects satisfying the contract. No prose, confidence, task IDs, absolute task-specific coordinates, or test answers. The first character of your response must be [ and the last character must be ]."""
        stage = "repair_call"
        repair_response, account = _call(client, task_id=task_id, attempt=3, prompt=repair_prompt, generation=GENERATION)
        accounts.append(account)
        raw_manifest.append({"phase": "repair", "cache_hit": repair_response.cache_hit, "response_text": repair_response.text})
        stage = "repair_parse"
        repaired = _json_slice(repair_response.text, "[", "]")
        if not isinstance(repaired, list):
            raise ValueError("repairer did not return a JSON list")
        stage = "repair_contract"
        repair_contract = validate_candidate_contract(repaired)

        stage = "final_verify"
        final_score = verify_candidate_batch([*generated, *repaired], task["train"])
        return {
            "schema_version": 1,
            "task_id": task_id,
            "provider": PROVIDER,
            "model": MODEL,
            "default_model": DEFAULT_MODEL,
            "model_override_used": MODEL != DEFAULT_MODEL,
            "solver_version": "t0022-multi-candidate-v2-contract",
            "generation_settings": {"generate_repair": asdict(GENERATION), "critique_challenge": asdict(CRITIQUE)},
            "attempts": 4,
            "raw_phase_manifest": raw_manifest,
            "contract_validation": {"generation": generation_contract, "repair": repair_contract},
            "critique_manifest": critiques,
            "critique_the_critique_manifest": challenges,
            "pre_repair_verification": first_score,
            "final_verification": final_score,
            "accounting": merge_accounting(accounts),
            "public_evaluation_used": False,
        }
    except TargetProviderError:
        raise
    except Exception as exc:
        return _operational_failure(
            task_id=task_id,
            stage=stage,
            exc=exc,
            accounts=accounts,
            raw_manifest=raw_manifest,
        )


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
        result = {
            "schema_version": 1,
            "task_id": args.task_id,
            "status": "provider_failure",
            "provider": PROVIDER,
            "model": MODEL,
            "default_model": DEFAULT_MODEL,
            "model_override_used": MODEL != DEFAULT_MODEL,
            "provider_failure": {
                "message": str(exc),
                "status_code": exc.status_code,
                "retryable": exc.retryable,
                "terminal": not exc.retryable,
                "error_category": exc.error_category,
                "rate_limit_headers": exc.rate_limit_headers,
            },
            "public_evaluation_used": False,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
