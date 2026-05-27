"""Decorator to coerce function arguments to specified types."""

import functools
from typing import Any, Callable, Dict, Type


def coerce_types(**coercions: Type) -> Callable[..., Any]:
    """Coerce keyword arguments to specified types before execution.

    Args:
        **coercions: Mapping of argument names to target types.

    Example:
        .. code-block:: python

           @coerce_types(age=int, active=bool)
           def process(age, active):
               ...

    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            coerced = {}
            for name, target_type in coercions.items():
                if name in kwargs:
                    try:
                        coerced[name] = target_type(kwargs[name])
                    except (ValueError, TypeError) as e:
                        raise TypeError(
                            f"Cannot coerce argument '{name}' "
                            f"to {target_type.__name__}: {e}"
                        )
                else:
                    coerced[name] = kwargs.get(name)
            kwargs.update(coerced)
            return func(*args, **kwargs)

        return wrapper

    return decorator
