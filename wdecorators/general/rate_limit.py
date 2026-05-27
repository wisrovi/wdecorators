"""Decorator that limits the rate of function calls."""

import functools
import logging
import time
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def rate_limit(calls_per_second: float) -> Callable[..., Any]:
    """Limit the rate of function calls, delaying excess calls.

    Args:
        calls_per_second: Maximum number of calls per second.

    Example:
        .. code-block:: python

           @rate_limit(calls_per_second=2)
           def say_hello(name):
               return f"Hello, {name}!"

    """
    interval = 1.0 / calls_per_second
    last_call = [0.0]

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            elapsed = time.perf_counter() - last_call[0]
            if elapsed < interval:
                sleep_time = interval - elapsed
                logger.debug(
                    "Rate limiting %s, sleeping %.3fs", func.__name__, sleep_time
                )
                time.sleep(sleep_time)
            last_call[0] = time.perf_counter()
            return func(*args, **kwargs)

        return wrapper

    return decorator
