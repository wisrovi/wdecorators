"""Decorator that measures and logs function execution duration."""

import asyncio
import functools
import logging
import time
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def time_execution(func: Callable[..., Any]) -> Callable[..., Any]:
    """Measure and log the execution duration of the decorated function.

    Alias for benchmark, supports both sync and async functions.

    Example:
        .. code-block:: python

           @time_execution
           def slow_function():
               time.sleep(1.5)

    """
    is_async = asyncio.iscoroutinefunction(func)

    if is_async:

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            logger.info("%s took %.6fs", func.__name__, elapsed)
            return result

        return async_wrapper

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info("%s took %.6fs", func.__name__, elapsed)
        return result

    return wrapper
