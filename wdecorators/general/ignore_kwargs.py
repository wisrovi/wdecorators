"""Decorator to silently ignore specified keyword arguments."""

import functools
from typing import Any, Callable, Set


def ignore_kwargs(*names: str) -> Callable[..., Any]:
    """Silently ignore specified keyword arguments passed to the function.

    Args:
        *names: Names of keyword arguments to ignore.

    Example:
        .. code-block:: python

           @ignore_kwargs('unused_param', 'deprecated_option')
           def process(data):
               ...

    """
    ignored: Set[str] = set(names)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            filtered = {k: v for k, v in kwargs.items() if k not in ignored}
            return func(*args, **filtered)

        return wrapper

    return decorator
