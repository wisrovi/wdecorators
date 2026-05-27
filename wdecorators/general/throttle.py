"""Decorator that throttles function calls by dropping excess calls."""

import functools
import time
from typing import Any, Callable


def throttle(interval: float) -> Callable[..., Any]:
    """Throttle function calls: only one call per `interval` seconds is allowed.

    Excess calls are silently dropped (unlike rate_limit which delays).

    Args:
        interval: Minimum seconds between calls.

    Example:
        .. code-block:: python

           @throttle(interval=1.0)
           def on_scroll(position):
               print("Scroll position:", position)

    """
    last_call = [0.0]

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.monotonic()
            if now - last_call[0] >= interval:
                last_call[0] = now
                return func(*args, **kwargs)
            return None

        return wrapper

    return decorator
