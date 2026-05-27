"""Decorator that catches exceptions and logs them."""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger("wdecorators")


def log_exceptions(
    func: Optional[Callable[..., Any]] = None, *, fallback: Any = None
) -> Callable[..., Any]:
    """Catch exceptions, log them, and return a fallback value.

    Can be used with or without arguments:
        @log_exceptions
        def foo(): ...

        @log_exceptions(fallback=None)
        def bar(): ...

    Supports both sync and async functions.

    Args:
        func: The decorated function (used when called without arguments).
        fallback: Value to return on exception.
    """

    def _decorate(f: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(f)

        if is_async:

            @functools.wraps(f)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    logger.error("Error in %s: %s", f.__name__, e)
                    return fallback

            return async_wrapper

        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error("Error in %s: %s", f.__name__, e)
                return fallback

        return wrapper

    if func is not None:
        return _decorate(func)

    return _decorate
