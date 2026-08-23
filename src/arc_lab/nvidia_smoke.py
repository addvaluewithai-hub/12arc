from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .target_model import CachedTargetClient, GenerationConfig, NvidiaNIMProvider, TargetRequest

ACTIVE_MODELS = (
    "deepseek-ai/deepseek-v4-flash-0731",
    "nvidia/nemotron-3-ultra-550b-a55b",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_smoke(*, cache_dir: Path, report_path: Path) -> dict:
    provider = NvidiaNIMProvider()
    client = CachedTargetClient(provider, cache_dir)
    records = []

    for model in ACTIVE_MODELS:
        request = TargetRequest(
            model=model,
            prompt="This is a non-benchmark infrastructure check. Reply with exactly OK.",
            solver_version="nvidia-adapter-smoke-v1",
            task_id="non-benchmark-nvidia-smoke",
            attempt_index=0,
            generation=GenerationConfig(
                temperature=0.0,
                top_p=1.0,
                top_k=None,
                max_output_tokens=128,
            ),
        )
        cache_key = request.fingerprint(provider.provider_id)
        first = client.generate(request)
        second = client.generate(request)
        cache_path = cache_dir / f"{cache_key}.json"

        if first.cache_hit:
            raise RuntimeError(f"first {model} call unexpectedly came from cache")
        if not second.cache_hit:
            raise RuntimeError(f"second {model} call did not reuse deterministic cache")
        if not first.text.strip():
            raise RuntimeError(f"{model} returned empty visible text")
        if first.model_resolved and first.model_resolved != model:
            raise RuntimeError(
                f"{model} resolved unexpectedly as {first.model_resolved}"
            )
        if first.text != second.text:
            raise RuntimeError(f"cached {model} response differs from live response")
        if not cache_path.exists():
            raise RuntimeError(f"cache file missing for {model}")

        metadata = first.provider_metadata or {}
        records.append(
            {
                "provider": provider.provider_id,
                "model_requested": model,
                "model_resolved": first.model_resolved,
                "visible_text_chars": len(first.text),
                "visible_text_preview": first.text[:80],
                "input_tokens": first.input_tokens,
                "output_tokens": first.output_tokens,
                "total_tokens": first.total_tokens,
                "runtime_seconds": first.runtime_seconds,
                "finish_reason": metadata.get("finish_reason"),
                "reasoning_chars": metadata.get("reasoning_chars"),
                "rate_limit_headers": metadata.get("rate_limit_headers", {}),
                "live_cache_hit": first.cache_hit,
                "repeat_cache_hit": second.cache_hit,
                "provider_requests_required": 1,
                "request_fingerprint": cache_key,
                "cache_sha256": _sha256(cache_path),
            }
        )

    report = {
        "schema_version": 1,
        "purpose": "provider-neutral NVIDIA NIM adapter/cache smoke; non-ARC",
        "provider": provider.provider_id,
        "secret_persisted": False,
        "models": records,
        "verified": all(
            record["repeat_cache_hit"]
            and not record["live_cache_hit"]
            and record["visible_text_chars"] > 0
            for record in records
        ),
        "provider_requests_total": len(records),
        "cache_hits_total": len(records),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = run_smoke(cache_dir=args.cache_dir, report_path=args.report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
