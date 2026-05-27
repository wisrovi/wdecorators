"""Decorator that debounces function calls."""

import functools
import threading
import time
from typing import Any, Callable, Optional


def debounce(wait: float, immediate: bool = False) -> Callable[..., Any]:
    """Debounce a function so it is called after `wait` seconds since the last call.

    If `immediate` is True, the first call is immediate and subsequent calls
    are debounced.

    Args:
        wait: Seconds to wait before calling the function.
        immediate: If True, call immediately on the first invocation.

    Example:
        .. code-block:: python

           @debounce(wait=0.5)
           def on_input(value):
               print("Processing:", value)

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        lock = threading.Lock()
        timer: Optional[threading.Timer] = None
        call_count = 0

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> None:
            nonlocal timer, call_count

            with lock:
                call_count += 1
                is_first_call = call_count == 1

                if timer is not None:
                    timer.cancel()
                    timer = None

                if immediate and is_first_call:
                    func(*args, **kwargs)
                else:

                    def delayed_call():
                        nonlocal timer
                        with lock:
                            func(*args, **kwargs)
                            timer = None

                    timer = threading.Timer(wait, delayed_call)
                    timer.daemon = True
                    timer.start()

        return wrapper

    return decorator
