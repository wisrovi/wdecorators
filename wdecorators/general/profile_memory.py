import functools
import tracemalloc
from typing import Any, Callable


def profile_memory(func: Callable) -> Callable:
    """Decorator that traces memory usage of the decorated function using tracemalloc."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(
            f"Memory usage - current: {current / 1024:.2f} KB, peak: {peak / 1024:.2f} KB"
        )
        return result

    return wrapper
