"""Tests for transform decorator."""

import pytest
from wdecorators import transform


def test_transform():
    @transform(str.strip)
    @transform(str.lower)
    def get_name():
        return "  ALICE  "

    assert get_name() == "alice"


def test_transform_multiple():
    @transform(lambda x: x * 2)
    def get_value():
        return 21

    assert get_value() == 42


def test_transform_single():
    @transform(str.upper)
    def greet():
        return "hello"

    assert greet() == "HELLO"


@pytest.mark.asyncio
async def test_transform_async():
    @transform(str.strip)
    @transform(str.lower)
    async def get_name():
        return "  ALICE  "

    result = await get_name()
    assert result == "alice"


@pytest.mark.asyncio
async def test_transform_async_single():
    @transform(lambda x: x * 3)
    async def get_value():
        return 10

    result = await get_value()
    assert result == 30


@pytest.mark.asyncio
async def test_transform_async_chained_sync():
    @transform(str.upper)
    async def get_msg():
        return "good bye"

    result = await get_msg()
    assert result == "GOOD BYE"
