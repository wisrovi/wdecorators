import functools
import os
import pickle
from typing import Any, Callable, Optional


def disk_cache(filename: str = "cache.pkl") -> Callable:
    """Decorator that caches function return values to disk using pickle.

    Args:
        filename: Path to the pickle cache file.
    """

    def decorator(func: Callable) -> Callable:
        cache: dict = {}
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                cache = pickle.load(f)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))
            if key in cache:
                return cache[key]
            result = func(*args, **kwargs)
            cache[key] = result
            with open(filename, "wb") as f:
                pickle.dump(cache, f)
            return result

        return wrapper

    return decorator
