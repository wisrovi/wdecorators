"""Decorator to suppress specific exceptions with an optional fallback."""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional, Tuple, Type

logger = logging.getLogger("wdecorators")


def suppress(
    *exceptions: Type[Exception], fallback: Any = None, log: bool = True
) -> Callable[..., Any]:
    """Suppress specified exceptions and return a fallback value.

    Args:
        *exceptions: Exception types to suppress.
        fallback: Value to return when an exception is caught.
        log: Whether to log suppressed exceptions.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           @suppress(ValueError, ZeroDivisionError, fallback=0)
           def divide(a, b):
               return a / b

    """
    if not exceptions:
        exceptions = (Exception,)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if log:
                        logger.warning(
                            "Suppressed %s in %s: %s",
                            type(e).__name__,
                            func.__name__,
                            e,
                        )
                    return fallback

            return async_wrapper
        else:

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if log:
                        logger.warning(
                            "Suppressed %s in %s: %s",
                            type(e).__name__,
                            func.__name__,
                            e,
                        )
                    return fallback

            return wrapper

    return decorator
