import functools
from typing import Any, Callable, Optional


def log_exceptions(func: Callable = None, *, fallback: Any = None) -> Callable:
    """Decorator that catches exceptions, prints them, and returns a fallback value.

    Can be used with or without arguments:
        @log_exceptions
        def foo(): ...

        @log_exceptions(fallback=None)
        def bar(): ...
    """
    if func is not None:

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error in {func.__name__}: {e}")
                return None

        return wrapper

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return f(*args, **kwargs)
            except Exception as e:
                print(f"Error in {f.__name__}: {e}")
                return fallback

        return wrapper

    return decorator
