"""Tests for repeat decorator."""

import pytest

from wdecorators import repeat


def test_repeat_sync():
    call_count = [0]

    @repeat(times=3, delay=0.01)
    def poll():
        call_count[0] += 1
        return call_count[0]

    results = poll()
    assert results == [1, 2, 3]
    assert call_count[0] == 3


@pytest.mark.asyncio
async def test_repeat_async():
    call_count = [0]

    @repeat(times=3, delay=0.01)
    async def poll():
        call_count[0] += 1
        return call_count[0]

    results = await poll()
    assert results == [1, 2, 3]
