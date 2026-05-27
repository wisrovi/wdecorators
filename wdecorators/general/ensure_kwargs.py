"""Decorator that forces all arguments to be passed as keyword arguments."""

import functools
import inspect
from typing import Any, Callable


def ensure_kwargs(func: Callable[..., Any]) -> Callable[..., Any]:
    """Convert positional arguments to keyword arguments.

    This allows a function to receive positional arguments while still
    working with functions that expect keyword-only arguments.

    Example:
        .. code-block:: python

           @ensure_kwargs
           def connect(*, host, port):
               ...

           connect("localhost", 8080)  # Works as connect(host="localhost", port=8080)

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        for i, arg in enumerate(args):
            if i < len(param_names):
                name = param_names[i]
                kwargs[name] = arg
        return func(**kwargs)

    return wrapper
