"""Decorator that measures and logs function execution time."""

import asyncio
import functools
import logging
import time
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def benchmark(func: Callable[..., Any]) -> Callable[..., Any]:
    """Measure and log the execution time of the decorated function.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           @benchmark
           def slow_task():
               time.sleep(1)

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
