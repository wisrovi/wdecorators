"""Decorator that logs the return value of a function."""

import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def log_return(func: Callable[..., Any]) -> Callable[..., Any]:
    """Log the return value of the decorated function.

    Example:
        .. code-block:: python

           @log_return
           def square(n):
               return n * n

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        logger.info("%s returned %s", func.__name__, result)
        return result

    return wrapper
