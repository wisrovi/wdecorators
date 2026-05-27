import functools
from typing import Any, Callable


def count_calls(func: Callable) -> Callable:
    """Decorator that counts and prints how many times the function has been called."""
    func.call_count = 0

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wrapper.call_count += 1
        print(f"{func.__name__} called {wrapper.call_count} times")
        return func(*args, **kwargs)

    wrapper.call_count = 0
    return wrapper
