"""Tests for retry_on_exception decorator."""

import pytest
from wdecorators import retry_on_exception


def test_retry_on_exception_success():
    call_count = [0]

    @retry_on_exception(retries=3, delay=0.01, exceptions=(ValueError,))
    def may_fail():
        call_count[0] += 1
        if call_count[0] < 2:
            raise ValueError("Temp error")
        return "ok"

    assert may_fail() == "ok"
    assert call_count[0] == 2


def test_retry_on_exception_exhausted():
    @retry_on_exception(retries=2, delay=0.01)
    def always_fails():
        raise ValueError("Always fails")

    with pytest.raises(RuntimeError):
        always_fails()


def test_retry_specific_exception_not_caught():
    @retry_on_exception(retries=2, delay=0.01, exceptions=(ValueError,))
    def raises_type_error():
        raise TypeError("Not caught")

    with pytest.raises(TypeError):
        raises_type_error()


def test_retry_first_attempt_succeeds():
    @retry_on_exception(retries=3, delay=0.01)
    def always_ok():
        return 99

    assert always_ok() == 99


@pytest.mark.asyncio
async def test_retry_async_success():
    call_count = [0]

    @retry_on_exception(retries=3, delay=0.01, exceptions=(ValueError,))
    async def may_fail():
        call_count[0] += 1
        if call_count[0] < 2:
            raise ValueError("Temp error")
        return "ok"

    result = await may_fail()
    assert result == "ok"
    assert call_count[0] == 2


@pytest.mark.asyncio
async def test_retry_async_exhausted():
    @retry_on_exception(retries=2, delay=0.01)
    async def always_fails():
        raise ValueError("Always fails")

    with pytest.raises(RuntimeError):
        await always_fails()


@pytest.mark.asyncio
async def test_retry_async_specific_exception_not_caught():
    @retry_on_exception(retries=2, delay=0.01, exceptions=(ValueError,))
    async def raises_type_error():
        raise TypeError("Not caught")

    with pytest.raises(TypeError):
        await raises_type_error()


@pytest.mark.asyncio
async def test_retry_async_first_attempt_succeeds():
    @retry_on_exception(retries=3, delay=0.01)
    async def always_ok():
        return 99

    result = await always_ok()
    assert result == 99
