"""Decorator that calls a callback function when an error occurs."""

import asyncio
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def notify_on_error(callback: Callable[[Exception], Any]) -> Callable[..., Any]:
    """Execute a callback when the decorated function raises an exception.

    The original exception is re-raised after the callback.

    Args:
        callback: Function called with the exception as argument.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           def send_alert(error):
               print(f"Alert: {error}")

           @notify_on_error(send_alert)
           def critical_operation():
               raise RuntimeError("Failed")

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error("Error in %s, notifying callback", func.__name__)
                    callback(e)
                    raise

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error("Error in %s, notifying callback", func.__name__)
                callback(e)
                raise

        return wrapper

    return decorator
