from types import SimpleNamespace

from arc_lab.target_model import GoogleGenAIProvider


def test_response_diagnostics_capture_thought_usage_without_thought_text():
    response = SimpleNamespace(
        usage_metadata=SimpleNamespace(
            prompt_token_count=100,
            candidates_token_count=None,
            thoughts_token_count=2048,
            total_token_count=2148,
        ),
        candidates=[SimpleNamespace(
            finish_reason="MAX_TOKENS",
            finish_message="budget exhausted",
            token_count=None,
            content=SimpleNamespace(parts=[SimpleNamespace(
                thought=True,
                text="secret chain of thought",
                thought_signature=b"opaque-signature",
            )]),
        )],
    )

    diagnostics = GoogleGenAIProvider.response_diagnostics(response)

    assert diagnostics["usage"]["thoughts_token_count"] == 2048
    assert diagnostics["usage"]["candidates_token_count"] is None
    assert diagnostics["candidates"][0]["finish_reason"] == "MAX_TOKENS"
    part = diagnostics["candidates"][0]["parts"][0]
    assert part == {
        "thought": True,
        "has_text": True,
        "text_chars": len("secret chain of thought"),
        "has_thought_signature": True,
    }
    assert "secret chain of thought" not in str(diagnostics)
    assert "opaque-signature" not in str(diagnostics)
