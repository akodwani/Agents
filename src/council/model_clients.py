from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

from jsonschema import ValidationError, validate
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_exponential

DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_RETRY_ATTEMPTS = 3
DISABLE_PAID_CALLS_ENV = "COUNCIL_DISABLE_PAID_CALLS"


class ModelClient(Protocol):
    def complete(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Generate a completion and validate it against the given JSON schema."""


class BudgetManager(Protocol):
    def on_request(self, *, client_name: str, prompt: str, schema: dict[str, Any]) -> None:
        """Called before every request to track spend/usage."""


@dataclass(slots=True)
class NoopBudgetManager:
    def on_request(self, *, client_name: str, prompt: str, schema: dict[str, Any]) -> None:  # pragma: no cover
        return None


class PaidCallsDisabledError(RuntimeError):
    """Raised when a paid API call is attempted while disabled by env flag."""


class ResponseFormatError(RuntimeError):
    """Raised when upstream model output cannot be parsed as JSON."""


class BaseModelClient(ABC):
    def __init__(
        self,
        *,
        budget_manager: BudgetManager | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
    ) -> None:
        self._budget_manager = budget_manager or NoopBudgetManager()
        self._timeout_seconds = timeout_seconds
        self._retry_attempts = retry_attempts

    @property
    @abstractmethod
    def client_name(self) -> str:
        ...

    @property
    def is_paid(self) -> bool:
        return True

    def complete(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        self._budget_manager.on_request(client_name=self.client_name, prompt=prompt, schema=schema)

        if self.is_paid and _paid_calls_disabled():
            raise PaidCallsDisabledError(
                f"Paid model calls are disabled by {DISABLE_PAID_CALLS_ENV}."
            )

        @retry(
            reraise=True,
            stop=stop_after_attempt(self._retry_attempts),
            wait=wait_exponential(multiplier=0.2, min=0.2, max=2),
            retry=retry_if_exception_type(
                (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ResponseFormatError)
            ),
        )
        def _complete_with_retry() -> dict[str, Any]:
            return self._complete_once(prompt=prompt, schema=schema)

        try:
            result = _complete_with_retry()
        except RetryError as exc:  # pragma: no cover
            raise RuntimeError("Model completion failed after retries") from exc

        validate(instance=result, schema=schema)
        return result

    @abstractmethod
    def _complete_once(self, *, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        ...


class OpenAIModelClient(BaseModelClient):
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        budget_manager: BudgetManager | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
    ) -> None:
        super().__init__(
            budget_manager=budget_manager,
            timeout_seconds=timeout_seconds,
            retry_attempts=retry_attempts,
        )
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._model = model
        self._base_url = base_url.rstrip("/")

    @property
    def client_name(self) -> str:
        return "openai"

    def _complete_once(self, *, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIModelClient")

        payload = {
            "model": self._model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": "Return valid JSON matching the provided schema.",
                },
                {"role": "user", "content": prompt},
            ],
        }

        response_json = self._post_completion(payload)
        content = (
            response_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content")
        )

        if not isinstance(content, str):
            raise ResponseFormatError("OpenAI response did not include message content")

        return json.loads(content)

    def _post_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url=f"{self._base_url}/chat/completions",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
        return json.loads(response_body)


class AnthropicModelClient(BaseModelClient):
    @property
    def client_name(self) -> str:
        return "anthropic"

    def _complete_once(self, *, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("AnthropicModelClient is still stubbed")


class StubModelClient(BaseModelClient):
    def __init__(
        self,
        *,
        name: str = "stub",
        budget_manager: BudgetManager | None = None,
    ) -> None:
        super().__init__(budget_manager=budget_manager)
        self._name = name

    @property
    def client_name(self) -> str:
        return self._name

    @property
    def is_paid(self) -> bool:
        return False

    def _complete_once(self, *, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"{self._name} model adapter is still stubbed")


def _paid_calls_disabled() -> bool:
    value = os.getenv(DISABLE_PAID_CALLS_ENV, "").strip().lower()
    return value in {"1", "true", "yes", "on"}
