import functools
import threading
import time
from typing import Any, Callable, Optional


def periodic_execution(interval: float) -> Callable:
    """Decorator that runs the decorated function periodically in a background thread.

    Args:
        interval: Time in seconds between each execution.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> threading.Thread:
            stop_event = threading.Event()

            def run():
                while not stop_event.is_set():
                    func(*args, **kwargs)
                    stop_event.wait(timeout=interval)

            thread = threading.Thread(target=run, daemon=True)
            thread.start()
            thread.stop_event = stop_event
            return thread

        return wrapper

    return decorator
