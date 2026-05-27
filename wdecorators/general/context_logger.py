"""Decorator that adds contextual logging with function metadata."""

import functools
import logging
from typing import Any, Callable, Optional


def context_logger(name: Optional[str] = None) -> Callable[..., Any]:
    """Add contextual logging that logs function entry/exit with timing.

    Args:
        name: Optional custom logger name. Defaults to the function's module.

    Example:
        .. code-block:: python

           @context_logger()
           def process_order(order_id):
               ...

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        log = logging.getLogger(name or func.__module__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log.info("Entering %s", func.__name__)
            try:
                result = func(*args, **kwargs)
                log.info("Exiting %s", func.__name__)
                return result
            except Exception as e:
                log.error("Error in %s: %s", func.__name__, e)
                raise

        return wrapper

    return decorator
