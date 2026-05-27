import functools
import time
from typing import Any, Callable


def rate_limit(calls_per_second: float) -> Callable:
    """Decorator that limits the number of calls per second to the decorated function.

    Args:
        calls_per_second: Maximum number of calls allowed per second.
    """
    interval = 1.0 / calls_per_second
    last_call = [0.0]

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            elapsed = time.perf_counter() - last_call[0]
            if elapsed < interval:
                time.sleep(interval - elapsed)
            last_call[0] = time.perf_counter()
            return func(*args, **kwargs)

        return wrapper

    return decorator
