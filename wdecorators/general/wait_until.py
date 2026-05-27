"""Decorator that waits for a condition before executing the function."""

import asyncio
import functools
import time
from typing import Any, Callable, Optional


def wait_until(
    predicate: Callable[[], bool], timeout: float = -1, interval: float = 0.1
) -> Callable[..., Any]:
    """Wait for a predicate to return True before executing the function.

    Args:
        predicate: A callable that returns a boolean.
        timeout: Maximum seconds to wait (-1 for no timeout).
        interval: Seconds between predicate checks.

    Raises:
        TimeoutError: If the timeout is exceeded.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           @wait_until(lambda: server.is_ready(), timeout=10)
           def process():
               ...

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        def _wait() -> None:
            start = time.monotonic()
            while not predicate():
                if timeout > 0 and (time.monotonic() - start) > timeout:
                    raise TimeoutError(
                        f"Timeout waiting for predicate in {func.__name__}"
                    )
                time.sleep(interval)

        async def _async_wait() -> None:
            start = time.monotonic()
            while not predicate():
                if timeout > 0 and (time.monotonic() - start) > timeout:
                    raise TimeoutError(
                        f"Timeout waiting for predicate in {func.__name__}"
                    )
                await asyncio.sleep(interval)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                await _async_wait()
                return await func(*args, **kwargs)

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _wait()
            return func(*args, **kwargs)

        return wrapper

    return decorator
