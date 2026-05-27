import functools
import signal
from typing import Any, Callable


class TimeoutException(Exception):
    """Raised when a timeout is exceeded."""

    pass


def timeout(seconds: int) -> Callable:
    """Decorator that raises TimeoutException if the function takes longer than `seconds`.

    Note: Uses SIGALRM which only works on Unix-like systems.
    On Windows, consider using the threading-based fallback.

    Args:
        seconds: Maximum allowed execution time in seconds.
    """

    def decorator(func: Callable) -> Callable:
        def handler(signum: int, frame: Any) -> None:
            raise TimeoutException(f"Function timed out after {seconds}s")

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        return wrapper

    return decorator
