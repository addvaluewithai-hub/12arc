from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class GenerationConfig:
    temperature: float = 1.0
    top_p: float | None = 0.95
    top_k: int | None = 64
    max_output_tokens: int = 256
    reasoning_effort: str | None = None


@dataclass(frozen=True)
class TargetRequest:
    model: str
    prompt: str
    solver_version: str
    task_id: str
    attempt_index: int
    generation: GenerationConfig = GenerationConfig()

    def fingerprint(self, provider_id: str | None = None) -> str:
        payload: dict[str, Any] = asdict(self)
        if provider_id is not None:
            payload["provider_id"] = provider_id
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode()).hexdigest()


@dataclass
class TargetResponse:
    model_requested: str
    model_resolved: str | None
    text: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    runtime_seconds: float
    cache_hit: bool = False
    provider_metadata: dict[str, Any] | None = None


class TargetProviderError(RuntimeError):
    """Sanitized provider failure carrying retry/rate-limit metadata."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        retryable: bool = False,
        rate_limit_headers: dict[str, str] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable
        self.rate_limit_headers = rate_limit_headers or {}


class TargetProvider(Protocol):
    provider_id: str

    def generate(self, request: TargetRequest) -> TargetResponse: ...


class CachedTargetClient:
    def __init__(
        self,
        provider: TargetProvider,
        cache_dir: str | Path,
        *,
        min_live_call_interval_seconds: float = 0.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ):
        if min_live_call_interval_seconds < 0:
            raise ValueError("min_live_call_interval_seconds must be non-negative")
        self.provider = provider
        self.cache_dir = Path(cache_dir)
        self.min_live_call_interval_seconds = min_live_call_interval_seconds
        self._clock = clock
        self._sleep = sleep
        self._last_live_call_started: float | None = None

    @property
    def provider_id(self) -> str:
        value = getattr(self.provider, "provider_id", None)
        if not isinstance(value, str) or not value:
            return self.provider.__class__.__name__
        return value

    def _wait_for_live_slot(self) -> None:
        if self._last_live_call_started is None:
            return
        elapsed = self._clock() - self._last_live_call_started
        remaining = self.min_live_call_interval_seconds - elapsed
        if remaining > 0:
            self._sleep(remaining)

    def generate(self, request: TargetRequest) -> TargetResponse:
        key = request.fingerprint(self.provider_id)
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            payload = json.loads(path.read_text())
            payload["cache_hit"] = True
            return TargetResponse(**payload)

        self._wait_for_live_slot()
        self._last_live_call_started = self._clock()
        response = self.provider.generate(request)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        payload = asdict(response)
        payload["cache_hit"] = False
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return response


class NvidiaNIMProvider:
    provider_id = "nvidia-nim"
    default_endpoint = "https://integrate.api.nvidia.com/v1/chat/completions"

    def __init__(
        self,
        api_key: str | None = None,
        *,
        endpoint: str | None = None,
        timeout_seconds: float = 120.0,
    ):
        key = api_key or os.environ.get("NVIDIA_API_KEY")
        if not key:
            raise RuntimeError("NVIDIA_API_KEY is required")
        self._api_key = key
        self.endpoint = endpoint or self.default_endpoint
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _safe_error_payload(body: str) -> dict[str, Any] | None:
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        error = data.get("error")
        if isinstance(error, dict):
            return {
                "type": error.get("type"),
                "code": error.get("code"),
                "message": str(error.get("message", ""))[:500],
            }
        if error is not None:
            return {"message": str(error)[:500]}
        return None

    @staticmethod
    def _rate_limit_headers(headers: Any) -> dict[str, str]:
        if headers is None:
            return {}
        try:
            items = headers.items()
        except AttributeError:
            return {}
        return {
            str(key).lower(): str(value)
            for key, value in items
            if str(key).lower().startswith("x-ratelimit")
            or str(key).lower() == "retry-after"
        }

    def generate(self, request: TargetRequest) -> TargetResponse:
        generation = request.generation
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": generation.temperature,
            "max_tokens": generation.max_output_tokens,
            "stream": False,
        }
        if generation.top_p is not None:
            payload["top_p"] = generation.top_p
        if generation.top_k is not None:
            payload["top_k"] = generation.top_k
        if generation.reasoning_effort is not None:
            payload["reasoning_effort"] = generation.reasoning_effort

        http_request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        started = time.perf_counter()
        try:
            with urllib.request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                status = response.status
                body = response.read().decode("utf-8", errors="replace")
                headers = response.headers
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            safe_error = self._safe_error_payload(body)
            detail = safe_error or {"message": body[:500]}
            raise TargetProviderError(
                f"NVIDIA NIM HTTP {exc.code}: {detail}",
                status_code=exc.code,
                retryable=exc.code in {408, 429, 500, 502, 503, 504, 529},
                rate_limit_headers=self._rate_limit_headers(exc.headers),
            ) from exc
        except Exception as exc:
            raise TargetProviderError(
                f"NVIDIA NIM transport failure: {type(exc).__name__}: {exc}",
                retryable=True,
            ) from exc

        runtime = time.perf_counter() - started
        if status != 200:
            raise TargetProviderError(
                f"NVIDIA NIM unexpected HTTP status {status}",
                status_code=status,
                retryable=status in {408, 429, 500, 502, 503, 504, 529},
                rate_limit_headers=self._rate_limit_headers(headers),
            )
        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError("NVIDIA NIM returned non-JSON response") from exc
        if not isinstance(data, dict):
            raise RuntimeError("NVIDIA NIM returned unexpected response shape")

        choices = data.get("choices") or []
        first = choices[0] if choices else {}
        message = first.get("message") or {} if isinstance(first, dict) else {}
        text = message.get("content") or "" if isinstance(message, dict) else ""
        reasoning = ""
        if isinstance(message, dict):
            reasoning = message.get("reasoning_content") or message.get("reasoning") or ""
        usage = data.get("usage") or {}
        if not isinstance(usage, dict):
            usage = {}

        rate_headers = self._rate_limit_headers(headers)
        return TargetResponse(
            model_requested=request.model,
            model_resolved=data.get("model"),
            text=text if isinstance(text, str) else str(text),
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            runtime_seconds=runtime,
            provider_metadata={
                "provider": self.provider_id,
                "endpoint": self.endpoint,
                "finish_reason": first.get("finish_reason") if isinstance(first, dict) else None,
                "reasoning_chars": len(reasoning) if isinstance(reasoning, str) else 0,
                "usage_details": {
                    key: value
                    for key, value in usage.items()
                    if key not in {"prompt_tokens", "completion_tokens", "total_tokens"}
                },
                "rate_limit_headers": rate_headers,
            },
        )


class GoogleGenAIProvider:
    provider_id = "google-genai"

    def __init__(self, api_key: str | None = None):
        try:
            from google import genai
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("install the 'gemma' optional dependency") from exc

        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is required")
        self._client = genai.Client(api_key=key)

    @staticmethod
    def _get(value: Any, name: str) -> Any:
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get(name)
        return getattr(value, name, None)

    @staticmethod
    def _enum_value(value: Any) -> Any:
        if value is None:
            return None
        return getattr(value, "value", value if isinstance(value, (str, int, float, bool)) else str(value))

    @classmethod
    def response_diagnostics(cls, response: Any) -> dict[str, Any]:
        """Return sanitized response structure without persisting thought text/signatures."""
        usage = cls._get(response, "usage_metadata")
        candidates = cls._get(response, "candidates") or []
        candidate_records: list[dict[str, Any]] = []
        for candidate in candidates:
            content = cls._get(candidate, "content")
            parts = cls._get(content, "parts") or []
            part_records: list[dict[str, Any]] = []
            for part in parts:
                text = cls._get(part, "text")
                signature = cls._get(part, "thought_signature")
                part_records.append(
                    {
                        "thought": cls._get(part, "thought"),
                        "has_text": isinstance(text, str) and bool(text),
                        "text_chars": len(text) if isinstance(text, str) else 0,
                        "has_thought_signature": bool(signature),
                    }
                )
            candidate_records.append(
                {
                    "finish_reason": cls._enum_value(cls._get(candidate, "finish_reason")),
                    "finish_message": cls._get(candidate, "finish_message"),
                    "token_count": cls._get(candidate, "token_count"),
                    "parts": part_records,
                }
            )
        return {
            "usage": {
                "prompt_token_count": cls._get(usage, "prompt_token_count"),
                "candidates_token_count": cls._get(usage, "candidates_token_count"),
                "thoughts_token_count": cls._get(usage, "thoughts_token_count"),
                "total_token_count": cls._get(usage, "total_token_count"),
            },
            "candidates": candidate_records,
        }

    def resolve_model(self, model: str) -> dict[str, Any]:
        info = self._client.models.get(model=model)
        return {
            "name": self._get(info, "name"),
            "display_name": self._get(info, "display_name"),
            "version": self._get(info, "version"),
        }

    def generate(self, request: TargetRequest) -> TargetResponse:
        from google.genai import types

        model_info = self.resolve_model(request.model)
        started = time.perf_counter()
        response = self._client.models.generate_content(
            model=request.model,
            contents=request.prompt,
            config=types.GenerateContentConfig(
                temperature=request.generation.temperature,
                top_p=request.generation.top_p,
                top_k=request.generation.top_k,
                max_output_tokens=request.generation.max_output_tokens,
            ),
        )
        runtime = time.perf_counter() - started
        usage = self._get(response, "usage_metadata")
        resolved = self._get(response, "model_version") or model_info.get("name")
        try:
            text = response.text or ""
        except (AttributeError, ValueError):
            text = ""
        return TargetResponse(
            model_requested=request.model,
            model_resolved=resolved,
            text=text,
            input_tokens=self._get(usage, "prompt_token_count"),
            output_tokens=self._get(usage, "candidates_token_count"),
            total_tokens=self._get(usage, "total_token_count"),
            runtime_seconds=runtime,
            provider_metadata={
                "provider": self.provider_id,
                "model": model_info,
                "response_diagnostics": self.response_diagnostics(response),
            },
        )
