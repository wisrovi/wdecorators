import functools
import json
from typing import Any, Callable


def to_json(func: Callable) -> Callable:
    """Decorator that converts the return value of the function to a JSON string."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        return json.dumps(func(*args, **kwargs))

    return wrapper
