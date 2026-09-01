"""Tests for _utils helper functions."""

import asyncio

from wdecorators.general._utils import (
    decorator_with_optional_args,
    is_async,
    make_async_wrapper,
    update_wrapper_with_logging,
)


def test_is_async_sync():
    def sync_func():
        pass

    assert is_async(sync_func) is False


def test_is_async_async():
    async def async_func():
        pass

    assert is_async(async_func) is True


def test_make_async_wrapper():
    async def async_func():
        return 42

    async def wrapper_func(*args, **kwargs):
        return await async_func(*args, **kwargs)

    wrapped = make_async_wrapper(async_func, wrapper_func)
    result = asyncio.run(wrapped())
    assert result == 42
    assert wrapped.__name__ == async_func.__name__


def test_update_wrapper_with_logging():
    def wrapped():
        """Docstring."""
        return "original"

    def wrapper():
        return "wrapper"

    updated = update_wrapper_with_logging(wrapper, wrapped)
    assert updated.__name__ == "wrapped"
    assert updated.__doc__ == "docstring"
    assert updated.__wrapped__ is wrapped


def test_decorator_with_optional_args_with_func():
    def my_decorator(func):
        def inner():
            return "decorated"

        return inner

    def my_func():
        return "func"

    result = decorator_with_optional_args(my_decorator, my_func)
    assert result is not None


def test_decorator_with_optional_args_without_func():
    def my_decorator(func=None):
        if func is not None:

            def inner():
                return "decorated"

            return inner
        return my_decorator

    result = decorator_with_optional_args(my_decorator, None)
    assert result is my_decorator
