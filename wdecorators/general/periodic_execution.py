"""Decorator that runs a function periodically in a background thread."""

import functools
import logging
import threading
import time
from typing import Any, Callable

logger = logging.getLogger("wdecorators")


def periodic_execution(interval: float) -> Callable[..., Any]:
    """Run the decorated function periodically in a background thread.

    The returned thread has a `stop_event` threading.Event that can be set
    to stop the periodic execution.

    Args:
        interval: Time in seconds between each execution.

    Example:
        .. code-block:: python

           @periodic_execution(interval=5)
           def heartbeat():
               print("Alive...")

           thread = heartbeat()
           time.sleep(12)
           thread.stop_event.set()

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
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
