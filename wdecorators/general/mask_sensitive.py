"""Decorator to mask sensitive argument values in logs and outputs."""

import functools
import logging
from typing import Any, Callable, Optional, Set, Tuple

logger = logging.getLogger("wdecorators")


def mask_sensitive(
    *args_to_mask: str, mask_char: str = "*", show_last: int = 0
) -> Callable[..., Any]:
    """Mask sensitive argument values when logging function calls.

    Args:
        *args_to_mask: Names of arguments to mask.
        mask_char: Character to use for masking.
        show_last: Number of unmasked characters to show at the end.

    Example:
        .. code-block:: python

           @mask_sensitive('password', 'token', show_last=2)
           def login(username, password, token):
               return "OK"

           login("alice", "secret123", "abcde")
           # Logs: Calling login with args=... password='******23', ...

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            masked_kwargs = {}
            for k, v in kwargs.items():
                if k in args_to_mask and isinstance(v, str):
                    visible = v[-show_last:] if show_last > 0 else ""
                    masked = mask_char * max(0, len(v) - show_last)
                    masked_kwargs[k] = masked + visible
                else:
                    masked_kwargs[k] = v

            logger.debug(
                "Calling %s with args=%s, kwargs=%s", func.__name__, args, masked_kwargs
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator
