"""Decorator to mark functions as deprecated."""

import functools
import warnings
from typing import Any, Callable, Optional


def deprecated(
    version: Optional[str] = None,
    alternative: Optional[str] = None,
    reason: Optional[str] = None,
) -> Callable[..., Any]:
    """Mark a function as deprecated, emitting a warning when called.

    Args:
        version: Version when the function was deprecated.
        alternative: Name of the replacement function.
        reason: Additional deprecation reason.

    Example:
        .. code-block:: python

           @deprecated(version='1.0.0', alternative='new_function')
           def old_function():
               ...

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        message = f"{func.__name__} is deprecated"
        if version:
            message += f" since version {version}"
        if alternative:
            message += f", use {alternative} instead"
        if reason:
            message += f" ({reason})"

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator
