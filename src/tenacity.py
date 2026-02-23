from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable


class RetryError(Exception):
    pass


@dataclass
class _StopAfterAttempt:
    attempts: int

    def should_stop(self, attempt_number: int) -> bool:
        return attempt_number >= self.attempts


def stop_after_attempt(attempts: int) -> _StopAfterAttempt:
    return _StopAfterAttempt(attempts=attempts)


@dataclass
class _WaitExponential:
    multiplier: float = 1.0
    min: float = 0.0
    max: float = 60.0

    def wait(self, attempt_number: int) -> float:
        amount = self.multiplier * (2 ** (attempt_number - 1))
        return max(self.min, min(self.max, amount))


def wait_exponential(*, multiplier: float = 1.0, min: float = 0.0, max: float = 60.0) -> _WaitExponential:
    return _WaitExponential(multiplier=multiplier, min=min, max=max)


@dataclass
class _RetryIfExceptionType:
    exception_types: tuple[type[BaseException], ...]

    def should_retry(self, exc: BaseException) -> bool:
        return isinstance(exc, self.exception_types)


def retry_if_exception_type(exception_types):
    if not isinstance(exception_types, tuple):
        exception_types = (exception_types,)
    return _RetryIfExceptionType(exception_types=exception_types)


def retry(*, reraise: bool, stop: _StopAfterAttempt, wait: _WaitExponential, retry: _RetryIfExceptionType):
    def decorator(fn: Callable):
        def wrapped(*args, **kwargs):
            attempt = 0
            while True:
                attempt += 1
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    if (not retry.should_retry(exc)) or stop.should_stop(attempt):
                        if reraise:
                            raise
                        raise RetryError() from exc
                    time.sleep(wait.wait(attempt))

        return wrapped

    return decorator
