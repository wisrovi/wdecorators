"""Decorator to repeat a function call multiple times."""

import asyncio
import functools
import time
from typing import Any, Callable, List, Optional, Union


def repeat(times: int, delay: Union[int, float] = 0) -> Callable[..., Any]:
    """Repeat the decorated function call N times and collect results.

    Args:
        times: Number of times to execute the function.
        delay: Seconds to wait between executions.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           @repeat(times=3, delay=0.5)
           def poll():
               return check_status()

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> List[Any]:
                results = []
                for i in range(times):
                    result = await func(*args, **kwargs)
                    results.append(result)
                    if i < times - 1 and delay > 0:
                        await asyncio.sleep(delay)
                return results

            return async_wrapper
        else:

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> List[Any]:
                results = []
                for i in range(times):
                    result = func(*args, **kwargs)
                    results.append(result)
                    if i < times - 1 and delay > 0:
                        time.sleep(delay)
                return results

            return wrapper

    return decorator
