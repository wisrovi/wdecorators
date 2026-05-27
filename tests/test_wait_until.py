"""Tests for wait_until decorator."""

import asyncio

import pytest
from wdecorators import wait_until


def test_wait_until_predicate_satisfied_immediately():
    flag = [True]

    @wait_until(lambda: flag[0], timeout=1)
    def my_func():
        return 42

    assert my_func() == 42


def test_wait_until_predicate_becomes_true():
    flag = [False]

    @wait_until(lambda: flag[0], timeout=1)
    def my_func():
        return 99

    def resolve():
        flag[0] = True

    import threading
    threading.Timer(0.05, resolve).start()
    result = my_func()
    assert result == 99


def test_wait_until_timeout():
    @wait_until(lambda: False, timeout=0.2)
    def my_func():
        return "never"

    with pytest.raises(TimeoutError, match="Timeout waiting for predicate in my_func"):
        my_func()


def test_wait_until_no_timeout_never_satisfied():
    with pytest.raises(TimeoutError):

        @wait_until(lambda: False, timeout=0.2)
        def my_func():
            return "never"

        my_func()


def test_wait_until_custom_interval():
    flag = [False]

    @wait_until(lambda: flag[0], timeout=1, interval=0.01)
    def my_func():
        return "ok"

    flag[0] = True
    assert my_func() == "ok"


def test_wait_until_negative_timeout_no_timeout():
    flag = [True]

    @wait_until(lambda: flag[0], timeout=-1)
    def my_func():
        return "no timeout"

    assert my_func() == "no timeout"


@pytest.mark.asyncio
async def test_wait_until_async_predicate_satisfied_immediately():
    flag = [True]

    @wait_until(lambda: flag[0], timeout=1)
    async def my_func():
        return 42

    result = await my_func()
    assert result == 42


@pytest.mark.asyncio
async def test_wait_until_async_predicate_becomes_true():
    flag = [False]

    @wait_until(lambda: flag[0], timeout=1)
    async def my_func():
        return 77

    async def resolve():
        await asyncio.sleep(0.05)
        flag[0] = True

    asyncio.create_task(resolve())
    result = await my_func()
    assert result == 77


@pytest.mark.asyncio
async def test_wait_until_async_timeout():
    @wait_until(lambda: False, timeout=0.2)
    async def my_func():
        return "never"

    with pytest.raises(TimeoutError, match="Timeout waiting for predicate in my_func"):
        await my_func()


@pytest.mark.asyncio
async def test_wait_until_async_negative_timeout():
    flag = [True]

    @wait_until(lambda: flag[0], timeout=-1)
    async def my_func():
        return "async no timeout"

    result = await my_func()
    assert result == "async no timeout"
