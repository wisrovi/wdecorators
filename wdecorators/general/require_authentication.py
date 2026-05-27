import functools
from typing import Any, Callable, Dict


def require_authentication(user: Dict[str, bool]) -> Callable:
    """Decorator that checks if a user dict has 'authenticated' set to True.

    Args:
        user: A dict with an 'authenticated' boolean key.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not user.get("authenticated", False):
                raise PermissionError("Access denied: user not authenticated")
            return func(*args, **kwargs)

        return wrapper

    return decorator
