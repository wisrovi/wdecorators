"""Cross-platform timeout decorator with SIGALRM and threading fallback."""

import asyncio
import functools
import platform
import threading
from typing import Any, Callable


class TimeoutException(Exception):
    """Raised when a timeout is exceeded."""

    pass


def timeout(seconds: float) -> Callable[..., Any]:
    """Raise TimeoutException if the function takes longer than `seconds`.

    Uses SIGALRM on Unix (accurate) and threading on Windows (fallback).

    Supports both sync and async functions.

    Args:
        seconds: Maximum allowed execution time in seconds.

    Example:
        .. code-block:: python

           @timeout(2)
           def long_task():
               time.sleep(5)

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return await asyncio.wait_for(
                        func(*args, **kwargs), timeout=seconds
                    )
                except asyncio.TimeoutError:
                    raise TimeoutException(
                        f"Function '{func.__name__}' timed out after {seconds}s"
                    )

            return async_wrapper

        if platform.system() != "Windows":
            import signal

            @functools.wraps(func)
            def unix_wrapper(*args: Any, **kwargs: Any) -> Any:
                def handler(signum: int, frame: Any) -> None:
                    raise TimeoutException(
                        f"Function '{func.__name__}' timed out after {seconds}s"
                    )

                old_handler = signal.signal(signal.SIGALRM, handler)
                signal.alarm(int(seconds))
                try:
                    return func(*args, **kwargs)
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)

            return unix_wrapper

        @functools.wraps(func)
        def windows_wrapper(*args: Any, **kwargs: Any) -> Any:
            result_container = []
            exception_container = []
            event = threading.Event()

            def target():
                try:
                    result_container.append(func(*args, **kwargs))
                except Exception as e:
                    exception_container.append(e)
                finally:
                    event.set()

            thread = threading.Thread(target=target, daemon=True)
            thread.start()

            if not event.wait(timeout=seconds):
                raise TimeoutException(
                    f"Function '{func.__name__}' timed out after {seconds}s"
                )

            if exception_container:
                raise exception_container[0]

            return result_container[0]

        return windows_wrapper

    return decorator
