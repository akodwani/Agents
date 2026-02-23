import json

import pytest
from jsonschema import ValidationError

from council.model_clients import (
    DISABLE_PAID_CALLS_ENV,
    AnthropicModelClient,
    OpenAIModelClient,
    PaidCallsDisabledError,
)


class RecordingBudgetManager:
    def __init__(self):
        self.calls = []

    def on_request(self, *, client_name, prompt, schema):
        self.calls.append({"client_name": client_name, "prompt": prompt, "schema": schema})


def test_openai_client_parses_and_validates_json(monkeypatch):
    budget = RecordingBudgetManager()
    client = OpenAIModelClient(api_key="test", budget_manager=budget)

    def fake_post_completion(payload):
        assert payload["model"] == "gpt-4o-mini"
        return {
            "choices": [
                {"message": {"content": json.dumps({"answer": "ok", "score": 3})}}
            ]
        }

    monkeypatch.setattr(client, "_post_completion", fake_post_completion)

    schema = {
        "type": "object",
        "properties": {
            "answer": {"type": "string"},
            "score": {"type": "number"},
        },
        "required": ["answer", "score"],
        "additionalProperties": False,
    }
    result = client.complete("hello", schema)
    assert result == {"answer": "ok", "score": 3}
    assert budget.calls and budget.calls[0]["client_name"] == "openai"


def test_openai_client_enforces_schema(monkeypatch):
    client = OpenAIModelClient(api_key="test")

    monkeypatch.setattr(
        client,
        "_post_completion",
        lambda payload: {"choices": [{"message": {"content": json.dumps({"answer": 1})}}]},
    )

    schema = {
        "type": "object",
        "properties": {"answer": {"type": "string"}},
        "required": ["answer"],
    }

    with pytest.raises(ValidationError):
        client.complete("hello", schema)


def test_paid_calls_can_be_disabled(monkeypatch):
    budget = RecordingBudgetManager()
    client = OpenAIModelClient(api_key="test", budget_manager=budget)
    monkeypatch.setenv(DISABLE_PAID_CALLS_ENV, "true")

    with pytest.raises(PaidCallsDisabledError):
        client.complete("hello", {"type": "object"})

    assert len(budget.calls) == 1


def test_stubbed_clients_stay_stubbed():
    client = AnthropicModelClient()
    with pytest.raises(NotImplementedError):
        client.complete("hello", {"type": "object"})
