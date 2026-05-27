import functools
from typing import Any, Callable


def debug_arguments(func: Callable) -> Callable:
    """Decorator that prints the arguments and keyword arguments passed to the function."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        return func(*args, **kwargs)

    return wrapper
