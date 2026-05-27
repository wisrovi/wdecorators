"""Decorator that traces memory usage of a function."""

import functools
import logging
import tracemalloc
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def profile_memory(func: Callable[..., Any]) -> Callable[..., Any]:
    """Trace memory usage of the decorated function using tracemalloc.

    Example:
        .. code-block:: python

           @profile_memory
           def create_list():
               return [i for i in range(100000)]

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        logger.info(
            "Memory in %s - current: %.2f KB, peak: %.2f KB",
            func.__name__,
            current / 1024,
            peak / 1024,
        )
        return result

    return wrapper
