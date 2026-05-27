"""Decorator to validate positional argument types at runtime."""

import functools
import logging
from typing import Any, Callable, Tuple, Type

logger = logging.getLogger("wdecorators")


def accepts(*types: Type) -> Callable[..., Any]:
    """Validate that positional arguments match the given types.

    Args:
        *types: Expected types for each positional argument.

    Raises:
        TypeError: If any positional argument does not match its expected type.

    Example:
        .. code-block:: python

           @accepts(int, int)
           def add(a, b):
               return a + b

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for i, (arg, expected) in enumerate(zip(args, types)):
                if not isinstance(arg, expected):
                    raise TypeError(
                        f"Argument {i} of {func.__name__} expected "
                        f"{expected.__name__}, got {type(arg).__name__}"
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator
