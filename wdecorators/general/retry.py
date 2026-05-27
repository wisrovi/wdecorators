import functools
from typing import Any, Callable, Optional


def retry(times: int = 3) -> Callable:
    """Decorator that retries the decorated function up to `times` times on failure.

    Args:
        times: Maximum number of retry attempts.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Optional[Exception] = None
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"Attempt {attempt + 1}/{times} failed: {e}")
            print(f"All {times} attempts failed for {func.__name__}")
            return None

        return wrapper

    return decorator
