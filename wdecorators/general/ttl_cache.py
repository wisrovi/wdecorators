"""Decorator that caches function results with a TTL (time-to-live)."""

import functools
import time
from typing import Any, Callable, Dict, Optional, Tuple


def ttl_cache(seconds: int = 60, maxsize: int = 128) -> Callable[..., Any]:
    """Cache function results with a time-to-live.

    Args:
        seconds: Number of seconds the cache entry remains valid.
        maxsize: Maximum number of cache entries (LRU eviction).

    Example:
        .. code-block:: python

           @ttl_cache(seconds=30)
           def get_data():
               return expensive_call()

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache: Dict[Tuple, Any] = {}
        timestamps: Dict[Tuple, float] = {}
        access_order: list = []

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (args, tuple(sorted(kwargs.items())))
            now = time.monotonic()

            if key in cache:
                if now - timestamps[key] < seconds:
                    access_order.remove(key)
                    access_order.append(key)
                    return cache[key]
                else:
                    del cache[key]
                    del timestamps[key]
                    access_order.remove(key)

            result = func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = now
            access_order.append(key)

            if len(cache) > maxsize:
                oldest = access_order.pop(0)
                del cache[oldest]
                del timestamps[oldest]

            return result

        def cache_clear() -> None:
            cache.clear()
            timestamps.clear()
            access_order.clear()

        wrapper.cache_clear = cache_clear  # type: ignore
        wrapper.cache_info = lambda: {  # type: ignore
            "size": len(cache),
            "maxsize": maxsize,
            "ttl": seconds,
        }

        return wrapper

    return decorator
