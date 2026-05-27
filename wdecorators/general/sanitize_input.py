import functools
import html
from typing import Any, Callable


def sanitize_input(func: Callable) -> Callable:
    """Decorator that HTML-escapes all string arguments passed to the function."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        clean_args = tuple(
            html.escape(str(a)) if isinstance(a, str) else a for a in args
        )
        clean_kwargs = {
            k: html.escape(str(v)) if isinstance(v, str) else v
            for k, v in kwargs.items()
        }
        return func(*clean_args, **clean_kwargs)

    return wrapper
