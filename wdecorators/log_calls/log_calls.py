import functools
from typing import Any, Callable


def log_calls(func: Callable) -> Callable:
    """Decorator that logs each call with its arguments and return value."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result

    return wrapper
