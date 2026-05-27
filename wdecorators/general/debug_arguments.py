"""Decorator that logs function arguments for debugging."""

import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def debug_arguments(func: Callable[..., Any]) -> Callable[..., Any]:
    """Log the arguments and keyword arguments passed to the function.

    Example:
        .. code-block:: python

           @debug_arguments
           def add(a, b):
               return a + b

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug("Calling %s with args=%s, kwargs=%s", func.__name__, args, kwargs)
        return func(*args, **kwargs)

    return wrapper
