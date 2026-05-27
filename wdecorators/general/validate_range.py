"""Decorator to validate numeric arguments are within a range."""

import functools
from typing import Any, Callable, Optional, Union


def validate_range(
    arg: str,
    minimum: Optional[Union[int, float]] = None,
    maximum: Optional[Union[int, float]] = None,
) -> Callable[..., Any]:
    """Validate that a numeric argument is within the specified range.

    Args:
        arg: Name of the argument to validate.
        minimum: Minimum allowed value (inclusive).
        maximum: Maximum allowed value (inclusive).

    Raises:
        ValueError: If the argument is outside the specified range.

    Example:
        .. code-block:: python

           @validate_range('value', minimum=0, maximum=100)
           def set_percentage(value):
               ...

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            all_args = _get_arg_dict(func, args, kwargs)
            if arg not in all_args:
                raise ValueError(f"Argument '{arg}' not found in {func.__name__}")
            value = all_args[arg]
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"Argument '{arg}' must be numeric, got {type(value).__name__}"
                )
            if minimum is not None and value < minimum:
                raise ValueError(
                    f"Argument '{arg}' = {value} is less than minimum {minimum}"
                )
            if maximum is not None and value > maximum:
                raise ValueError(
                    f"Argument '{arg}' = {value} is greater than maximum {maximum}"
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _get_arg_dict(func: Callable, args: tuple, kwargs: dict) -> dict:
    import inspect

    sig = inspect.signature(func)
    bound = sig.bind_partial(*args, **kwargs)
    bound.apply_defaults()
    return dict(bound.arguments)
