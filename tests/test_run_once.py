"""Tests for run_once decorator."""

import asyncio
from wdecorators import run_once


def test_run_once_executes_once():
    call_count = [0]

    @run_once
    def init():
        call_count[0] += 1
        return "ready"

    assert init() == "ready"
    assert init() == "ready"
    assert call_count[0] == 1


def test_run_once_caches_result():
    @run_once
    def compute():
        return 42

    assert compute() == 42
    assert compute() == 42


def test_run_once_different_args_return_cached():
    call_count = [0]

    @run_once
    def compute(*args, **kwargs):
        call_count[0] += 1
        return call_count[0]

    first = compute(1, 2, 3)
    second = compute(4, 5, 6)
    assert first == 1
    assert second == 1
    assert call_count[0] == 1


def test_run_once_async():
    call_count = [0]

    @run_once
    async def init():
        call_count[0] += 1
        return "ready"

    result1 = asyncio.run(init())
    result2 = asyncio.run(init())
    assert result1 == "ready"
    assert result2 == "ready"
    assert call_count[0] == 1
