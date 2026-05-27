"""Decorator to validate the return type of a function at runtime."""

import functools
from typing import Any, Callable, Type


def returns(expected_type: Type) -> Callable[..., Any]:
    """Validate that the function return value matches the given type.

    Args:
        expected_type: The expected return type.

    Raises:
        TypeError: If the return value does not match the expected type.

    Example:
        .. code-block:: python

           @returns(int)
           def get_id():
               return 42

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            if not isinstance(result, expected_type):
                raise TypeError(
                    f"{func.__name__} expected return type "
                    f"{expected_type.__name__}, got {type(result).__name__}"
                )
            return result

        return wrapper

    return decorator
