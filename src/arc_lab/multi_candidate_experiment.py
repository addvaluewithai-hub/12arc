from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from .multi_candidate import AccountingRecord, merge_accounting, verify_candidate_batch
from .multi_candidate_contract import prompt_contract_fragment, validate_candidate_contract
from .target_model import (
    CachedTargetClient,
    GenerationConfig,
    NvidiaNIMProvider,
    TargetProviderError,
    TargetRequest,
)
from .taskio import load_task

DEFAULT_MODEL = "deepseek-ai/deepseek-v4-flash-0731"
MODEL = os.environ.get("ARC_TARGET_MODEL", DEFAULT_MODEL)
PROVIDER = "nvidia-nim"
SOLVER_VERSION = "t0022-multi-candidate-v3-json-enforced"
GENERATION = GenerationConfig(temperature=0.7, top_p=0.95, top_k=64, max_output_tokens=4096)
CRITIQUE = GenerationConfig(temperature=0.2, top_p=0.95, top_k=64, max_output_tokens=3072)
JSON_REPAIR = GenerationConfig(temperature=0.0, top_p=1.0, top_k=None, max_output_tokens=4096)


class JsonContractError(ValueError):
    """The model response did not satisfy the executable JSON contract."""


def _json_slice(text: str, opening: str, closing: str, *, accept: Callable[[Any], bool] | None = None) -> Any:
    """Return the first valid JSON container of the requested kind.

    Hosted models often wrap JSON in prose or markdown. We scan the response for
    JSON values and return the first container that has the requested type and
    passes an optional semantic predicate. This is deterministic extraction, not
    model scoring.
    """

    expected_type = list if opening == "[" else dict
    decoder = json.JSONDecoder()
    failures: list[str] = []
    for start, char in enumerate(text):
        if char != opening:
            continue
        try:
            value, _end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError as exc:
            failures.append(f"offset={start}: {exc.msg}")
            continue
        if not isinstance(value, expected_type):
            failures.append(f"offset={start}: decoded {type(value).__name__}, expected {expected_type.__name__}")
            continue
        if accept is not None and not accept(value):
            failures.append(f"offset={start}: semantic predicate rejected container")
            continue
        return value
    preview = text[:500].replace("\n", "\\n")
    detail = "; ".join(failures[:5])
    suffix = f"; attempts={detail}" if detail else ""
    raise JsonContractError(
        f"response contains no parseable JSON {opening}{closing} container; preview={preview!r}{suffix}"
    )


def _call(
    client: CachedTargetClient,
    *,
    task_id: str,
    attempt: int,
    prompt: str,
    generation: GenerationConfig,
):
    request = TargetRequest(
        model=MODEL,
        prompt=prompt,
        solver_version=SOLVER_VERSION,
        task_id=task_id,
        attempt_index=attempt,
        generation=generation,
    )
    response = client.generate(request)
    accounting = AccountingRecord(
        request_count=0 if response.cache_hit else 1,
        cache_hits=1 if response.cache_hit else 0,
        input_tokens=response.input_tokens or 0,
        output_tokens=response.output_tokens or 0,
        total_tokens=response.total_tokens
        or ((response.input_tokens or 0) + (response.output_tokens or 0)),
        runtime_seconds=response.runtime_seconds,
    )
    return response, accounting


def _candidate_acceptor(*, expected_count: int | None = None, min_count: int = 1) -> Callable[[Any], bool]:
    def accept(value: Any) -> bool:
        if not isinstance(value, list):
            return False
        if len(value) < min_count:
            return False
        if expected_count is not None and len(value) != expected_count:
            return False
        if not all(isinstance(item, dict) for item in value):
            return False
        report = validate_candidate_contract(value)
        return report["contract_invalid_candidates"] == 0

    return accept


def _dict_key_acceptor(key: str) -> Callable[[Any], bool]:
    def accept(value: Any) -> bool:
        return isinstance(value, dict) and isinstance(value.get(key), list)

    return accept


def _parse_json_or_retry(
    client: CachedTargetClient,
    *,
    task_id: str,
    stage: str,
    raw_text: str,
    opening: str,
    closing: str,
    accept: Callable[[Any], bool] | None,
    retry_attempt: int,
    original_prompt: str,
    raw_manifest: list[dict[str, Any]],
    accounts: list[AccountingRecord],
    retry_instruction: str,
) -> Any:
    try:
        return _json_slice(raw_text, opening, closing, accept=accept)
    except Exception as first_exc:
        correction_prompt = f"""STRICT JSON CORRECTION TASK.

Your previous response for phase `{stage}` was INVALID because:
{type(first_exc).__name__}: {first_exc}

You must now return ONLY valid JSON. No markdown fences. No commentary. No analysis.
The first byte of the response MUST be `{opening}` and the final byte MUST be `{closing}`.

Required JSON contract:
{retry_instruction}

Original phase prompt:
{original_prompt}

Previous invalid response, for conversion only:
{raw_text[:12000]}
"""
        response, account = _call(
            client,
            task_id=task_id,
            attempt=retry_attempt,
            prompt=correction_prompt,
            generation=JSON_REPAIR,
        )
        accounts.append(account)
        raw_manifest.append(
            {
                "phase": f"{stage}_json_retry",
                "cache_hit": response.cache_hit,
                "response_text": response.text,
                "recovered_from_error": f"{type(first_exc).__name__}: {first_exc}",
            }
        )
        return _json_slice(response.text, opening, closing, accept=accept)


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
        "solver_version": SOLVER_VERSION,
        "failure_stage": stage,
        "error_type": type(exc).__name__,
        "error_message": str(exc)[:1000],
        "raw_phase_manifest": raw_manifest,
        "accounting": merge_accounting(accounts),
        "public_evaluation_used": False,
    }


def _candidate_json_instruction(*, count_text: str) -> str:
    return (
        f"Return a JSON array of {count_text} executable candidate objects. "
        "Every candidate must have exactly top-level keys schema_version and steps. "
        "schema_version must be integer 1 or 2, not a string. "
        "No instructions, strategy, program, prose, confidence, or extra keys. "
        "All steps must use only the allowed executable ops in the contract."
    )


def run(task_path: Path, *, task_id: str, cache_dir: Path) -> dict[str, Any]:
    task = load_task(task_path, require_test_outputs=False)
    train_json = json.dumps(task["train"], separators=(",", ":"))
    contract = prompt_contract_fragment()
    client = CachedTargetClient(
        NvidiaNIMProvider(timeout_seconds=900),
        cache_dir,
        min_live_call_interval_seconds=1.0,
    )
    accounts: list[AccountingRecord] = []
    raw_manifest: list[dict[str, Any]] = []
    stage = "initialize"

    try:
        generation_prompt = f"""You are an ARC executable-candidate JSON compiler.

Training pairs:
{train_json}

{contract}

HARD OUTPUT RULES:
- Return ONLY a JSON array.
- The first character MUST be [ and the last character MUST be ].
- The array MUST contain exactly 16 DISTINCT executable candidate objects.
- Do NOT explain, analyze, include markdown, include prose, or include confidence.
- Do NOT output `instructions`, `strategy`, `program`, or pseudocode.
- If uncertain, still output the closest valid executable JSON candidates using only the allowed schema.

Deterministic Python will execute and score the candidates."""
        stage = "generate_call"
        response, account = _call(
            client,
            task_id=task_id,
            attempt=0,
            prompt=generation_prompt,
            generation=GENERATION,
        )
        accounts.append(account)
        raw_manifest.append({"phase": "generate", "cache_hit": response.cache_hit, "response_text": response.text})
        stage = "generate_parse_or_retry"
        generated = _parse_json_or_retry(
            client,
            task_id=task_id,
            stage="generate",
            raw_text=response.text,
            opening="[",
            closing="]",
            accept=_candidate_acceptor(expected_count=16),
            retry_attempt=10,
            original_prompt=generation_prompt,
            raw_manifest=raw_manifest,
            accounts=accounts,
            retry_instruction=_candidate_json_instruction(count_text="exactly 16"),
        )
        stage = "generate_contract"
        generation_contract = validate_candidate_contract(generated)
        if generation_contract["contract_invalid_candidates"] != 0:
            raise JsonContractError(f"generation contract invalid: {generation_contract['failures'][:5]}")
        stage = "generate_verify"
        first_score = verify_candidate_batch(generated, task["train"])

        compact_scores = [
            {
                k: c[k]
                for k in (
                    "candidate_id",
                    "normalized_ir",
                    "exact_training_pairs",
                    "total_cell_error",
                    "structural_violations",
                )
            }
            for c in first_score["ranked_candidates"]
        ]
        critique_prompt = f"""Act as a falsifying critic, not a judge.

ARC training pairs:
{train_json}

Candidate Python metrics:
{json.dumps(compact_scores, separators=(",", ":"))}

Return ONLY a JSON object:
{{"critiques":[{{"candidate_id":"...","likely_failure":"...","violated_training_pair":0,"forbidden_constant_risk":"...","separator_or_unchanged_region_risk":"...","repair_suggestion":"..."}}]}}

HARD OUTPUT RULES:
- The first character MUST be {{ and the last character MUST be }}.
- No markdown, prose, or analysis outside the JSON object.
- Use Python metrics as evidence; do not claim correctness."""
        stage = "critique_call"
        critique_response, account = _call(
            client,
            task_id=task_id,
            attempt=1,
            prompt=critique_prompt,
            generation=CRITIQUE,
        )
        accounts.append(account)
        raw_manifest.append({"phase": "critique", "cache_hit": critique_response.cache_hit, "response_text": critique_response.text})
        stage = "critique_parse_or_retry"
        critiques = _parse_json_or_retry(
            client,
            task_id=task_id,
            stage="critique",
            raw_text=critique_response.text,
            opening="{",
            closing="}",
            accept=_dict_key_acceptor("critiques"),
            retry_attempt=11,
            original_prompt=critique_prompt,
            raw_manifest=raw_manifest,
            accounts=accounts,
            retry_instruction='Return exactly a JSON object with key "critiques" whose value is a JSON array.',
        )

        challenge_prompt = f"""Challenge these ARC candidate critiques for unsupported assumptions.

Training pairs:
{train_json}

Critiques:
{json.dumps(critiques, separators=(",", ":"))}

Return ONLY a JSON object:
{{"challenges":[{{"candidate_id":"...","critique_valid":true,"reason":"...","smallest_general_repair":"..."}}]}}

HARD OUTPUT RULES:
- The first character MUST be {{ and the last character MUST be }}.
- No markdown, prose, or analysis outside the JSON object.
- Do not choose a winner and do not invent execution results."""
        stage = "critique_the_critique_call"
        challenge_response, account = _call(
            client,
            task_id=task_id,
            attempt=2,
            prompt=challenge_prompt,
            generation=CRITIQUE,
        )
        accounts.append(account)
        raw_manifest.append(
            {
                "phase": "critique_the_critique",
                "cache_hit": challenge_response.cache_hit,
                "response_text": challenge_response.text,
            }
        )
        stage = "critique_the_critique_parse_or_retry"
        challenges = _parse_json_or_retry(
            client,
            task_id=task_id,
            stage="critique_the_critique",
            raw_text=challenge_response.text,
            opening="{",
            closing="}",
            accept=_dict_key_acceptor("challenges"),
            retry_attempt=12,
            original_prompt=challenge_prompt,
            raw_manifest=raw_manifest,
            accounts=accounts,
            retry_instruction='Return exactly a JSON object with key "challenges" whose value is a JSON array.',
        )

        repair_prompt = f"""You are an ARC executable-candidate JSON repair compiler.

Training pairs:
{train_json}

Original normalized candidates and metrics:
{json.dumps(compact_scores, separators=(",", ":"))}

Critiques:
{json.dumps(critiques, separators=(",", ":"))}

Challenges:
{json.dumps(challenges, separators=(",", ":"))}

{contract}

HARD OUTPUT RULES:
- Return ONLY a JSON array.
- The first character MUST be [ and the last character MUST be ].
- The array MUST contain between 1 and 8 repaired executable candidate objects.
- Do NOT explain the task.
- Do NOT analyze the examples.
- Do NOT include markdown.
- Do NOT output `instructions`, `strategy`, `program`, confidence, or pseudocode.
- Every candidate must be executable under the exact contract above.
- If unsure, emit simple valid executable variants rather than prose.

Deterministic Python will execute and score the repaired candidates."""
        stage = "repair_call"
        repair_response, account = _call(
            client,
            task_id=task_id,
            attempt=3,
            prompt=repair_prompt,
            generation=GENERATION,
        )
        accounts.append(account)
        raw_manifest.append({"phase": "repair", "cache_hit": repair_response.cache_hit, "response_text": repair_response.text})
        stage = "repair_parse_or_retry"
        repaired = _parse_json_or_retry(
            client,
            task_id=task_id,
            stage="repair",
            raw_text=repair_response.text,
            opening="[",
            closing="]",
            accept=_candidate_acceptor(expected_count=None, min_count=1),
            retry_attempt=13,
            original_prompt=repair_prompt,
            raw_manifest=raw_manifest,
            accounts=accounts,
            retry_instruction=_candidate_json_instruction(count_text="between 1 and 8"),
        )
        if len(repaired) > 8:
            raise JsonContractError(f"repair returned {len(repaired)} candidates, expected at most 8")
        stage = "repair_contract"
        repair_contract = validate_candidate_contract(repaired)
        if repair_contract["contract_invalid_candidates"] != 0:
            raise JsonContractError(f"repair contract invalid: {repair_contract['failures'][:5]}")

        stage = "final_verify"
        final_score = verify_candidate_batch([*generated, *repaired], task["train"])
        return {
            "schema_version": 1,
            "task_id": task_id,
            "provider": PROVIDER,
            "model": MODEL,
            "default_model": DEFAULT_MODEL,
            "model_override_used": MODEL != DEFAULT_MODEL,
            "solver_version": SOLVER_VERSION,
            "generation_settings": {
                "generate_repair": asdict(GENERATION),
                "critique_challenge": asdict(CRITIQUE),
                "json_repair": asdict(JSON_REPAIR),
            },
            "attempts": len(raw_manifest),
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
