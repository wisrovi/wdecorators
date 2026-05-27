"""Decorator that synchronizes function execution with a lock."""

import asyncio
import functools
import threading
from typing import Any, Callable, Optional


def synchronized(lock: Optional[threading.Lock] = None) -> Callable[..., Any]:
    """Ensure the decorated function is executed with a lock for thread safety.

    If no lock is provided, a module-level RLock is created per function.

    Args:
        lock: An optional threading.Lock object. If None, creates a new RLock.

    Supports both sync and async functions.

    Example:
        .. code-block:: python

           @synchronized()
           def critical_section():
               ...

    """
    func_lock = lock or threading.RLock()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                with func_lock:
                    return await func(*args, **kwargs)

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with func_lock:
                return func(*args, **kwargs)

        return wrapper

    return decorator
