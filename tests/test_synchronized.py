"""Tests for synchronized decorator."""

import asyncio
import threading

import pytest

from wdecorators import synchronized


def test_synchronized_thread_safety():
    counter = [0]

    @synchronized()
    def increment():
        current = counter[0]
        import time

        time.sleep(0.005)
        counter[0] = current + 1

    threads = [threading.Thread(target=increment) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert counter[0] == 20


def test_synchronized_with_custom_lock():
    custom_lock = threading.Lock()
    results = []

    @synchronized(lock=custom_lock)
    def append_item(item):
        results.append(item)

    threads = [threading.Thread(target=append_item, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(results) == list(range(10))


def test_synchronized_returns_value():
    @synchronized()
    def add(a, b):
        return a + b

    assert add(2, 3) == 5


@pytest.mark.asyncio
async def test_synchronized_async():
    results = []

    @synchronized()
    async def append_item(item):
        results.append(item)

    tasks = [asyncio.create_task(append_item(i)) for i in range(10)]
    await asyncio.gather(*tasks)

    assert sorted(results) == list(range(10))


@pytest.mark.asyncio
async def test_synchronized_async_with_custom_lock():
    custom_lock = threading.Lock()
    results = []

    @synchronized(lock=custom_lock)
    async def append_item(item):
        results.append(item)

    tasks = [asyncio.create_task(append_item(i)) for i in range(10)]
    await asyncio.gather(*tasks)

    assert sorted(results) == list(range(10))


@pytest.mark.asyncio
async def test_synchronized_async_returns_value():
    @synchronized()
    async def add(a, b):
        return a + b

    result = await add(2, 3)
    assert result == 5
