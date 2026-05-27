"""Decorator that retries function execution on failure."""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger("wdecorators")


def retry(times: int = 3) -> Callable[..., Any]:
    """Retry the decorated function up to `times` times on any exception.

    Supports both sync and async functions.

    Args:
        times: Maximum number of retry attempts.

    Example:
        .. code-block:: python

           @retry(times=5)
           def may_fail():
               import random
               if random.random() < 0.7:
                   raise ValueError("Random failure")
               return "Success"

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_error: Optional[Exception] = None
                for attempt in range(times):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_error = e
                        logger.warning(
                            "Attempt %d/%d failed for %s: %s",
                            attempt + 1,
                            times,
                            func.__name__,
                            e,
                        )
                logger.error("All %d attempts failed for %s", times, func.__name__)
                raise last_error  # type: ignore

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Optional[Exception] = None
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        "Attempt %d/%d failed for %s: %s",
                        attempt + 1,
                        times,
                        func.__name__,
                        e,
                    )
            logger.error("All %d attempts failed for %s", times, func.__name__)
            raise last_error  # type: ignore

        return wrapper

    return decorator
