"""Decorator that retries on specific exception types with delay."""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Tuple, Type

logger = logging.getLogger("wdecorators")


def retry_on_exception(
    retries: int = 3,
    delay: float = 2,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable[..., Any]:
    """Retry the function on specific exceptions with configurable delay.

    Supports both sync and async functions.

    Args:
        retries: Maximum number of retry attempts.
        delay: Seconds to wait between retries.
        exceptions: Tuple of exception types to catch and retry on.

    Raises:
        RuntimeError: If all retries are exhausted.

    Example:
        .. code-block:: python

           @retry_on_exception(retries=3, delay=1, exceptions=(ZeroDivisionError,))
           def risky_divide(x):
               return 10 / x

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                for i in range(retries):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        logger.warning(
                            "Attempt %d/%d failed: %s. Retrying in %ss...",
                            i + 1,
                            retries,
                            e,
                            delay,
                        )
                        if i < retries - 1:
                            await asyncio.sleep(delay)
                raise RuntimeError(
                    f"Function {func.__name__} failed after {retries} attempts."
                )

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(
                        "Attempt %d/%d failed: %s. Retrying in %ss...",
                        i + 1,
                        retries,
                        e,
                        delay,
                    )
                    if i < retries - 1:
                        time.sleep(delay)
            raise RuntimeError(
                f"Function {func.__name__} failed after {retries} attempts."
            )

        return wrapper

    return decorator
