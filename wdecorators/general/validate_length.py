"""Decorator to validate string/list argument lengths."""

import functools
from typing import Any, Callable, Optional


def validate_length(
    arg: str, minimum: Optional[int] = None, maximum: Optional[int] = None
) -> Callable[..., Any]:
    """Validate that a string/list argument length is within bounds.

    Args:
        arg: Name of the argument to validate.
        minimum: Minimum allowed length (inclusive).
        maximum: Maximum allowed length (inclusive).

    Raises:
        ValueError: If the argument length is outside the specified bounds.

    Example:
        .. code-block:: python

           @validate_length('name', minimum=1, maximum=50)
           def set_name(name):
               ...

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from .validate_range import _get_arg_dict

            all_args = _get_arg_dict(func, args, kwargs)
            if arg not in all_args:
                raise ValueError(f"Argument '{arg}' not found in {func.__name__}")
            value = all_args[arg]
            if not hasattr(value, "__len__"):
                raise TypeError(
                    f"Argument '{arg}' must have length, got {type(value).__name__}"
                )
            length = len(value)
            if minimum is not None and length < minimum:
                raise ValueError(
                    f"Argument '{arg}' length {length} is less than minimum {minimum}"
                )
            if maximum is not None and length > maximum:
                raise ValueError(
                    f"Argument '{arg}' length {length} exceeds maximum {maximum}"
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
