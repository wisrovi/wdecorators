import functools
import time
from typing import Any, Callable


def time_execution(func: Callable) -> Callable:
    """Decorator that measures and prints execution time of the decorated function."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f}s")
        return result

    return wrapper
