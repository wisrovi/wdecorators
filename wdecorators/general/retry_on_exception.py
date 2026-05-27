import functools
import time
from typing import Any, Callable, Tuple, Type


def retry_on_exception(
    retries: int = 3,
    delay: float = 2,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator that retries the function on specific exceptions.

    Args:
        retries: Maximum number of retry attempts.
        delay: Seconds to wait between retries.
        exceptions: Tuple of exception types to catch and retry on.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(
                        f"Attempt {i + 1}/{retries} failed: {e}. Retrying in {delay}s..."
                    )
                    if i < retries - 1:
                        time.sleep(delay)
            raise RuntimeError(
                f"Function {func.__name__} failed after {retries} attempts."
            )

        return wrapper

    return decorator
