"""Decorator that enforces authentication checks."""

import functools
from typing import Any, Callable, Dict


def require_authentication(user: Dict[str, bool]) -> Callable[..., Any]:
    """Require the user to be authenticated before executing the function.

    Args:
        user: A dict with an 'authenticated' boolean key.

    Raises:
        PermissionError: If the user is not authenticated.

    Example:
        .. code-block:: python

           user = {"authenticated": True}

           @require_authentication(user)
           def secret_info():
               return "Top secret"

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not user.get("authenticated", False):
                raise PermissionError(
                    f"Access denied: user not authenticated for {func.__name__}"
                )
            return func(*args, **kwargs)

        return wrapper

    return decorator
