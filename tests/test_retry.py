"""Tests for retry decorator."""

import asyncio
import pytest
from wdecorators import retry


def test_retry_success():
    call_count = [0]

    @retry(times=3)
    def may_fail():
        call_count[0] += 1
        if call_count[0] < 2:
            raise ValueError("Temporary error")
        return "success"

    result = may_fail()
    assert result == "success"
    assert call_count[0] == 2


def test_retry_exhausted():
    call_count = [0]

    @retry(times=3)
    def always_fails():
        call_count[0] += 1
        raise ValueError("Always fails")

    with pytest.raises(ValueError):
        always_fails()
    assert call_count[0] == 3


@pytest.mark.asyncio
async def test_retry_async():
    call_count = [0]

    @retry(times=3)
    async def may_fail():
        call_count[0] += 1
        if call_count[0] < 2:
            raise ValueError("Temporary error")
        return "success"

    result = await may_fail()
    assert result == "success"
    assert call_count[0] == 2


def test_retry_async_exhausted():
    call_count = [0]

    @retry(times=3)
    async def always_fails():
        call_count[0] += 1
        raise ValueError("Always fails")

    with pytest.raises(ValueError):
        asyncio.run(always_fails())
    assert call_count[0] == 3
