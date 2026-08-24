import io
import json
import urllib.error
from pathlib import Path
from unittest.mock import patch

import pytest

from arc_lab.max_reasoning_direct import (
    GENERATION,
    PROVIDER_TIMEOUT_SECONDS,
    TASK_ID,
    aggregate,
    output_token_bucket,
    validate_trigger,
)
from arc_lab.target_model import (
    GenerationConfig,
    NvidiaNIMProvider,
    TargetProviderError,
    TargetRequest,
)


class _FakeHTTPResponse:
    status = 200
    headers = {"X-RateLimit-Remaining": "37", "Content-Type": "application/json"}

    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode()


def test_max_reasoning_configuration_is_explicit():
    assert GENERATION.temperature == 0.0
    assert GENERATION.top_p == 1.0
    assert GENERATION.top_k is None
    assert GENERATION.reasoning_effort == "max"
    assert GENERATION.max_output_tokens == 16384
    assert PROVIDER_TIMEOUT_SECONDS == 900.0


def test_reasoning_effort_participates_in_request_fingerprint():
    common = dict(
        model="deepseek-ai/deepseek-v4-flash-0731",
        prompt="same prompt",
        solver_version="test",
        task_id="task:test0",
        attempt_index=0,
    )
    high = TargetRequest(
        **common,
        generation=GenerationConfig(max_output_tokens=16384, reasoning_effort="high"),
    )
    max_reasoning = TargetRequest(
        **common,
        generation=GenerationConfig(max_output_tokens=16384, reasoning_effort="max"),
    )
    assert high.fingerprint("nvidia-nim") != max_reasoning.fingerprint("nvidia-nim")


def test_nvidia_provider_sends_reasoning_effort_and_custom_timeout():
    captured = {}
    payload = {
        "model": "deepseek-ai/deepseek-v4-flash-0731",
        "choices": [{"finish_reason": "stop", "message": {"content": "[[1]]"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
    }

    def fake_urlopen(request, timeout):
        captured["payload"] = json.loads(request.data.decode())
        captured["timeout"] = timeout
        return _FakeHTTPResponse(payload)

    provider = NvidiaNIMProvider(api_key="test-secret", timeout_seconds=900.0)
    request = TargetRequest(
        model="deepseek-ai/deepseek-v4-flash-0731",
        prompt="solve",
        solver_version="test",
        task_id="task:test0",
        attempt_index=0,
        generation=GenerationConfig(
            temperature=0.0,
            top_p=1.0,
            top_k=None,
            max_output_tokens=16384,
            reasoning_effort="max",
        ),
    )
    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        response = provider.generate(request)

    assert captured["timeout"] == 900.0
    assert captured["payload"]["max_tokens"] == 16384
    assert captured["payload"]["reasoning_effort"] == "max"
    assert "top_k" not in captured["payload"]
    assert response.provider_metadata["rate_limit_headers"]["x-ratelimit-remaining"] == "37"


def test_nvidia_retryable_http_error_preserves_sanitized_rate_headers():
    error = urllib.error.HTTPError(
        "https://example.invalid",
        529,
        "overloaded",
        {"Retry-After": "7", "X-RateLimit-Remaining": "0"},
        io.BytesIO(b'{"error":{"message":"busy"}}'),
    )
    provider = NvidiaNIMProvider(api_key="test-secret")
    request = TargetRequest(
        model="deepseek-ai/deepseek-v4-flash-0731",
        prompt="solve",
        solver_version="test",
        task_id="task:test0",
        attempt_index=0,
    )
    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(TargetProviderError) as raised:
            provider.generate(request)

    assert raised.value.status_code == 529
    assert raised.value.retryable is True
    assert raised.value.rate_limit_headers["retry-after"] == "7"
    assert raised.value.rate_limit_headers["x-ratelimit-remaining"] == "0"
    assert "test-secret" not in str(raised.value)


@pytest.mark.parametrize(
    ("tokens", "bucket"),
    [
        (None, "unknown"),
        (4096, "<=4096"),
        (4097, "4097-8192"),
        (8192, "4097-8192"),
        (8193, "8193-16383"),
        (16383, "8193-16383"),
        (16384, "16384_cap"),
    ],
)
def test_output_token_buckets(tokens, bucket):
    assert output_token_bucket(tokens) == bucket


def test_trigger_requires_matching_claim_and_run_reservation(tmp_path: Path):
    shift = "shift-123"
    trigger = tmp_path / "trigger.json"
    queue = tmp_path / "queue.json"
    counter = tmp_path / "counter.json"
    trigger.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "task_id": TASK_ID,
                "run": "ARC-R026",
                "shift_id": shift,
                "requested_at": "2026-08-24T16:00:00+03:00",
            }
        )
    )
    queue.write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "id": TASK_ID,
                        "status": "claimed",
                        "claim": {"shift_id": shift},
                    }
                ]
            }
        )
    )
    counter.write_text(
        json.dumps(
            {
                "active_reservations": [
                    {"run": "ARC-R026", "task_id": TASK_ID, "shift_id": shift}
                ]
            }
        )
    )
    assert validate_trigger(trigger, queue, counter)["run"] == "ARC-R026"

    counter.write_text(json.dumps({"active_reservations": []}))
    with pytest.raises(ValueError, match="reservation"):
        validate_trigger(trigger, queue, counter)


def test_aggregate_mechanically_matches_comparator_and_recovery(tmp_path: Path):
    protocol = tmp_path / "protocol.json"
    comparator = tmp_path / "comparator.json"
    parts = tmp_path / "parts"
    output = tmp_path / "result.json"
    parts.mkdir()
    protocol.write_text(
        json.dumps(
            {
                "run": "ARC-R026",
                "manifest_sha256": "manifest",
                "task_ids": ["a", "b"],
            }
        )
    )
    comparator.write_text(
        json.dumps(
            {
                "run": "ARC-R016",
                "records": [
                    {"task_id": "a", "solved": True},
                    {"task_id": "b", "solved": False},
                ],
            }
        )
    )
    (parts / "task-a.json").write_text(
        json.dumps(
            {
                "task_id": "a",
                "first_attempt_solved": False,
                "operational_recovered_solved": True,
                "transport_failure_events": 1,
                "tests": [
                    {
                        "test_index": 0,
                        "attempts": [
                            {
                                "transport_attempt": 0,
                                "ok": False,
                                "rate_limit_headers": {"retry-after": "1"},
                            },
                            {
                                "transport_attempt": 1,
                                "ok": True,
                                "output_token_bucket": "4097-8192",
                                "finish_reason": "stop",
                                "rate_limit_headers": {},
                            },
                        ],
                    }
                ],
            }
        )
    )
    (parts / "task-b.json").write_text(
        json.dumps(
            {
                "task_id": "b",
                "first_attempt_solved": True,
                "operational_recovered_solved": True,
                "tests": [
                    {
                        "test_index": 0,
                        "attempts": [
                            {
                                "transport_attempt": 0,
                                "ok": True,
                                "output_token_bucket": "<=4096",
                                "finish_reason": "stop",
                                "rate_limit_headers": {},
                            }
                        ],
                    }
                ],
            }
        )
    )

    report = aggregate(protocol, parts, comparator, output)
    assert report["comparator"]["solved"] == 1
    assert report["primary_first_attempt"]["solved"] == 1
    assert report["primary_first_attempt"]["new_solves"] == ["b"]
    assert report["primary_first_attempt"]["regressions"] == ["a"]
    assert report["operational_with_transport_recovery"]["solved"] == 2
    assert report["output_token_length_buckets"]["<=4096"] == 1
    assert report["output_token_length_buckets"]["4097-8192"] == 1
    assert report["rate_limit_snapshots"][0]["headers"]["retry-after"] == "1"
