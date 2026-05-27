"""Decorator for persistent on-disk caching with multiple serialization formats."""

import functools
import json
import os
import pickle
from typing import Any, Callable, Dict, Optional, Tuple, Union


def disk_cache(
    filename: str = "cache.pkl", serializer: str = "pickle"
) -> Callable[..., Any]:
    """Cache function return values to disk using the specified serialization format.

    Args:
        filename: Path to the cache file.
        serializer: Serialization format ('pickle', 'json').

    Example:
        .. code-block:: python

           @disk_cache('cache.json', serializer='json')
           def get_data():
               return {"key": "value"}

    """
    if serializer not in ("pickle", "json"):
        raise ValueError(f"Unsupported serializer: {serializer}")

    def _load_cache() -> Dict:
        if not os.path.exists(filename):
            return {}
        try:
            with open(filename, "rb") as f:
                if serializer == "pickle":
                    return pickle.load(f)
                return json.loads(f.read().decode())
        except (pickle.UnpicklingError, json.JSONDecodeError, EOFError):
            return {}

    def _save_cache(cache: Dict) -> None:
        with open(filename, "wb") as f:
            if serializer == "pickle":
                pickle.dump(cache, f)
            else:
                f.write(json.dumps(cache, default=str).encode())

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache = _load_cache()

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal cache
            key = str((args, tuple(sorted(kwargs.items()))))
            if key in cache:
                return cache[key]
            result = func(*args, **kwargs)
            cache[key] = result
            _save_cache(cache)
            return result

        def cache_clear() -> None:
            nonlocal cache
            cache = {}
            if os.path.exists(filename):
                os.remove(filename)

        wrapper.cache_clear = cache_clear  # type: ignore

        return wrapper

    return decorator
