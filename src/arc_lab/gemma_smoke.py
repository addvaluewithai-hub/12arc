from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .target_model import CachedTargetClient, GoogleGenAIProvider, TargetRequest, TargetResponse


def _normalized_model_name(name: str | None) -> str | None:
    if name is None:
        return None
    return name.removeprefix("models/")


def validate_smoke(
    first: TargetResponse,
    second: TargetResponse,
    *,
    requested_model: str,
) -> None:
    if not first.text.strip():
        raise ValueError("live smoke returned no text")
    if first.cache_hit:
        raise ValueError("first smoke request unexpectedly came from cache")
    if second.cache_hit is not True:
        raise ValueError("identical second request did not hit deterministic cache")
    if second.text != first.text:
        raise ValueError("cached smoke response differs from live response")

    model_meta = (first.provider_metadata or {}).get("model") or {}
    catalog_name = _normalized_model_name(model_meta.get("name"))
    if catalog_name != requested_model:
        raise ValueError(
            f"provider catalog resolved {catalog_name!r}, expected {requested_model!r}"
        )
    if not first.model_resolved:
        raise ValueError("provider did not report a resolved model identifier")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m arc_lab.gemma_smoke")
    parser.add_argument("--model", default="gemma-4-26b-a4b-it")
    parser.add_argument("--cache-dir", default=".cache/arc-model-smoke")
    parser.add_argument("--report", default="artifacts/gemma-smoke.json")
    args = parser.parse_args(argv)

    request = TargetRequest(
        model=args.model,
        prompt=(
            "This is an infrastructure smoke test, not an ARC benchmark task. "
            "Return one short line confirming that text generation is available."
        ),
        solver_version="gemma-execution-path-v2",
        task_id="non-benchmark-smoke",
        attempt_index=0,
    )
    client = CachedTargetClient(GoogleGenAIProvider(), args.cache_dir)
    first = client.generate(request)
    second = client.generate(request)
    validate_smoke(first, second, requested_model=args.model)

    report = {
        "schema_version": 1,
        "purpose": "non-ARC infrastructure smoke test",
        "request_fingerprint": request.fingerprint(),
        "first_call": {
            **asdict(first),
            "text": "<redacted-non-benchmark-response>",
        },
        "second_call": {
            **asdict(second),
            "text": "<redacted-cached-response>",
        },
        "cache_verified": True,
    }
    path = Path(args.report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "model_requested": first.model_requested,
                "model_resolved": first.model_resolved,
                "input_tokens": first.input_tokens,
                "output_tokens": first.output_tokens,
                "total_tokens": first.total_tokens,
                "runtime_seconds": first.runtime_seconds,
                "cache_verified": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
