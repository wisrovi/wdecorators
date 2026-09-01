"""Tests for suppress decorator."""

import pytest

from wdecorators import suppress


def test_suppress_fallback():
    @suppress(ZeroDivisionError, fallback=0)
    def divide(a, b):
        return a / b

    assert divide(10, 2) == 5.0
    assert divide(10, 0) == 0


def test_suppress_raises_unlisted():
    @suppress(ValueError, fallback=None)
    def risky():
        raise TypeError("Not suppressed")

    with pytest.raises(TypeError):
        risky()


def test_suppress_no_exceptions_arg():
    @suppress(fallback="caught")
    def fail():
        raise ValueError("Any exception")

    assert fail() == "caught"


def test_suppress_log_false():
    @suppress(ValueError, fallback=0, log=False)
    def fail():
        raise ValueError("Silent")

    assert fail() == 0


def test_suppress_multiple_exception_types():
    @suppress(ValueError, TypeError, ZeroDivisionError, fallback="ok")
    def may_fail(val):
        if val == 1:
            raise ValueError("Bad value")
        elif val == 2:
            raise TypeError("Bad type")
        elif val == 3:
            return 1 / 0
        return "success"

    assert may_fail(1) == "ok"
    assert may_fail(2) == "ok"
    assert may_fail(3) == "ok"
    assert may_fail(4) == "success"


def test_suppress_returns_fallback_on_single_type():
    @suppress(ValueError, fallback="default")
    def fail():
        raise ValueError("Oops")

    assert fail() == "default"


@pytest.mark.asyncio
async def test_suppress_async():
    @suppress(ValueError, fallback="default")
    async def fetch():
        raise ValueError("API error")

    result = await fetch()
    assert result == "default"


@pytest.mark.asyncio
async def test_suppress_async_raises_unlisted():
    @suppress(ValueError, fallback=None)
    async def risky():
        raise TypeError("Not suppressed")

    with pytest.raises(TypeError):
        await risky()


@pytest.mark.asyncio
async def test_suppress_async_log_false():
    @suppress(ValueError, fallback=0, log=False)
    async def fail():
        raise ValueError("Silent")

    result = await fail()
    assert result == 0


@pytest.mark.asyncio
async def test_suppress_async_no_exceptions_arg():
    @suppress(fallback="caught")
    async def fail():
        raise ValueError("Any exception")

    result = await fail()
    assert result == "caught"


@pytest.mark.asyncio
async def test_suppress_async_multiple_exception_types():
    @suppress(ValueError, TypeError, ZeroDivisionError, fallback="ok")
    async def may_fail(val):
        if val == 1:
            raise ValueError("Bad value")
        elif val == 2:
            raise TypeError("Bad type")
        elif val == 3:
            return 1 / 0
        return "success"

    assert await may_fail(1) == "ok"
    assert await may_fail(2) == "ok"
    assert await may_fail(3) == "ok"
    assert await may_fail(4) == "success"
