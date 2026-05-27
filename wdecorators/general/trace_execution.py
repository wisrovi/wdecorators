"""Decorator that traces function entry and exit."""

import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def trace_execution(func: Callable[..., Any]) -> Callable[..., Any]:
    """Log entry and exit messages for the decorated function.

    Example:
        .. code-block:: python

           @trace_execution
           def multiply(a, b):
               return a * b

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug("Entering %s", func.__name__)
        result = func(*args, **kwargs)
        logger.debug("Exiting %s", func.__name__)
        return result

    return wrapper
