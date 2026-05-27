import functools
from typing import Any, Callable


def trace_execution(func: Callable) -> Callable:
    """Decorator that prints entry and exit trace messages for the function."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Entering {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Exiting {func.__name__}")
        return result

    return wrapper
