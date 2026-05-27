"""Decorator for conditional function execution."""

import asyncio
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def conditional(predicate: Callable[[], bool]) -> Callable[..., Any]:
    """Only execute the decorated function if the predicate returns True.

    Args:
        predicate: A callable that takes no arguments and returns a bool.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           @conditional(lambda: is_feature_enabled())
           def experimental_feature():
               ...

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                if predicate():
                    return await func(*args, **kwargs)
                logger.debug("Skipping %s (predicate returned False)", func.__name__)
                return None

            return async_wrapper
        else:

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if predicate():
                    return func(*args, **kwargs)
                logger.debug("Skipping %s (predicate returned False)", func.__name__)
                return None

            return wrapper

    return decorator
