"""Shared utilities for wdecorators decorators."""

import asyncio
import functools
import logging
from typing import Any, Callable, TypeVar, Union

T = TypeVar("T", bound=Callable[..., Any])

logger = logging.getLogger("wdecorators")


def is_async(func: Callable[..., Any]) -> bool:
    """Check if a function is a coroutine function or wrapped coroutine."""
    return asyncio.iscoroutinefunction(func)


def make_async_wrapper(
    async_func: Callable[..., Any], wrapper_func: Callable[..., Any]
) -> Callable[..., Any]:
    """Create an async wrapper that delegates to the wrapper logic."""

    @functools.wraps(async_func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        return await wrapper_func(*args, **kwargs)

    return async_wrapper


def update_wrapper_with_logging(
    wrapper: Callable[..., Any],
    wrapped: Callable[..., Any],
    assigned: tuple = functools.WRAPPER_ASSIGNMENTS,
    updated: tuple = functools.WRAPPER_UPDATES,
) -> Callable[..., Any]:
    """Update wrapper metadata and preserve __wrapped__."""
    wrapper = functools.update_wrapper(
        wrapper, wrapped, assigned=assigned, updated=updated
    )
    return wrapper


def decorator_with_optional_args(
    decorator: Callable[..., Any],
    func: Union[Callable[..., Any], None],
    *args: Any,
    **kwargs: Any,
) -> Callable[..., Any]:
    """Helper for decorators that can be used with or without arguments.

    Usage:
        def my_decorator(_func=None, *, option=None):
            return decorator_with_optional_args(my_decorator, _func, option=option)

    This allows both:
        @my_decorator
        @my_decorator(option=True)
    """
    if func is not None:
        return decorator(func)
    return decorator
