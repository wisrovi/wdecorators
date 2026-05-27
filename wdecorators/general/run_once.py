"""Decorator that ensures a function runs only once and caches its result."""

import asyncio
import functools
from typing import Any, Callable


def run_once(func: Callable[..., Any]) -> Callable[..., Any]:
    """Ensure the decorated function runs only once and caches the result.

    Subsequent calls return the cached result without re-executing.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           @run_once
           def initialize():
               print("Initializing...")
               return "ready"

    """
    has_run = False
    result = None

    is_async = asyncio.iscoroutinefunction(func)

    if is_async:

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal has_run, result
            if not has_run:
                result = await func(*args, **kwargs)
                has_run = True
            return result

        return async_wrapper

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        nonlocal has_run, result
        if not has_run:
            result = func(*args, **kwargs)
            has_run = True
        return result

    return wrapper
