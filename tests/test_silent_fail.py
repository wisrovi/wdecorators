"""Tests for silent_fail decorator."""

import pytest
from wdecorators import silent_fail


def test_silent_fail_success():
    @silent_fail
    def ok():
        return 42

    assert ok() == 42


def test_silent_fail_returns_none():
    @silent_fail
    def fail():
        raise ValueError("Error")

    assert fail() is None


@pytest.mark.asyncio
async def test_silent_fail_async():
    @silent_fail
    async def fail():
        raise ValueError("Error")

    result = await fail()
    assert result is None
