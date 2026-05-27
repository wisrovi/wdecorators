"""Tests for benchmark decorator."""

import pytest
from wdecorators import benchmark


def test_benchmark_sync():
    @benchmark
    def fast():
        return 42

    assert fast() == 42


@pytest.mark.asyncio
async def test_benchmark_async():
    @benchmark
    async def fast():
        return 42

    result = await fast()
    assert result == 42
