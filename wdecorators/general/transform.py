"""Decorator that transforms the return value of a function."""

import asyncio
import functools
from typing import Any, Callable


def transform(transform_func: Callable[[Any], Any]) -> Callable[..., Any]:
    """Transform the return value through a function.

    Args:
        transform_func: A callable that takes the original return value
                       and returns the transformed value.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           @transform(str.strip)
           @transform(str.lower)
           def get_name():
               return "  ALICE  "

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = await func(*args, **kwargs)
                return transform_func(result)

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            return transform_func(result)

        return wrapper

    return decorator
