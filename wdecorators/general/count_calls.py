"""Decorator that tracks how many times a function has been called."""

import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def count_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    """Track and log how many times the decorated function has been called.

    The call count is accessible via the `call_count` attribute.

    Example:
        .. code-block:: python

           @count_calls
           def say_hello(name):
               return f"Hello, {name}!"

           print(say_hello.call_count)  # 0 after first call

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wrapper.call_count += 1
        logger.debug("%s called %d times", func.__name__, wrapper.call_count)
        return func(*args, **kwargs)

    wrapper.call_count = 0
    return wrapper
