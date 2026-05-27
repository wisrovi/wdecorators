import functools
from typing import Any, Callable


def silent_fail(func: Callable) -> Callable:
    """Decorator that silences any exception and returns None instead."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception:
            return None

    return wrapper
