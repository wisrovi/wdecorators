"""Decorator to provide default values for keyword arguments."""

import functools
from typing import Any, Callable


def default_values(**defaults: Any) -> Callable[..., Any]:
    """Set default values for keyword arguments if not provided.

    Args:
        **defaults: Default values for keyword arguments.

    Example:
        .. code-block:: python

           @default_values(timeout=30, retries=3)
           def connect(timeout, retries):
               ...

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for key, value in defaults.items():
                if key not in kwargs:
                    kwargs[key] = value
            return func(*args, **kwargs)

        return wrapper

    return decorator
