import functools
from typing import Any, Callable


def log_return(func: Callable) -> Callable:
    """Decorator that prints the return value of the decorated function."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result

    return wrapper
