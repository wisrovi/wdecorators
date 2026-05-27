"""Decorator that HTML-escapes string arguments to prevent XSS."""

import functools
import html
from typing import Any, Callable, Tuple


def sanitize_input(func: Callable[..., Any]) -> Callable[..., Any]:
    """HTML-escape all string arguments passed to the function.

    This helps prevent XSS attacks when user input is rendered in HTML.

    Example:
        .. code-block:: python

           @sanitize_input
           def display_message(message):
               return f"Message: {message}"

           print(display_message("<script>alert('XSS')</script>"))
           # Message: &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        clean_args: Tuple[Any, ...] = tuple(
            html.escape(str(a)) if isinstance(a, str) else a for a in args
        )
        clean_kwargs = {
            k: html.escape(str(v)) if isinstance(v, str) else v
            for k, v in kwargs.items()
        }
        return func(*clean_args, **clean_kwargs)

    return wrapper
