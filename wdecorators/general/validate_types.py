"""Validate types decorator module."""

import functools
from typing import Any, Callable, Dict, Type


def validate_types(**expected_types: Type) -> Callable:
    """Decorator that validates keyword argument types at runtime.

    Args:
        **expected_types: Keyword arguments mapping parameter names to expected types.

    Raises:
        TypeError: If a validated argument does not match its expected type.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for arg_name, arg_value in kwargs.items():
                if arg_name in expected_types:
                    expected = expected_types[arg_name]
                    if not isinstance(arg_value, expected):
                        raise TypeError(
                            f"Argument '{arg_name}' must be {expected}, got {type(arg_value)}"
                        )
            return func(*args, **kwargs)

        return wrapper

    return decorator
