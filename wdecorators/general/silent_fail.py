"""Decorator that silences exceptions and returns None."""

import asyncio
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def silent_fail(func: Callable[..., Any]) -> Callable[..., Any]:
    """Silence any exception raised by the function and return None instead.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           @silent_fail
           def risky_operation():
               return 1 / 0

    """
    is_async = asyncio.iscoroutinefunction(func)

    if is_async:

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.debug("Silenced error in %s: %s", func.__name__, e)
                return None

        return async_wrapper

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.debug("Silenced error in %s: %s", func.__name__, e)
            return None

    return wrapper
