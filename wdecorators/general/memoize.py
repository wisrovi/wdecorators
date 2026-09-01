"""Memoize decorator module."""

import functools
from typing import Any, Callable


def memoize(func: Callable) -> Callable:
    """Decorator that caches function results in memory keyed by arguments."""
    cache: dict = {}

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper
