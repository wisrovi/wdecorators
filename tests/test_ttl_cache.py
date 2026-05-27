"""Tests for ttl_cache decorator."""

import time
from wdecorators import ttl_cache


def test_ttl_cache_caches_result():
    call_count = [0]

    @ttl_cache(seconds=60)
    def compute(n):
        call_count[0] += 1
        return n * n

    assert compute(5) == 25
    assert call_count[0] == 1
    assert compute(5) == 25
    assert call_count[0] == 1


def test_ttl_cache_different_args():
    call_count = [0]

    @ttl_cache(seconds=60)
    def add(a, b):
        call_count[0] += 1
        return a + b

    assert add(1, 2) == 3
    assert call_count[0] == 1
    assert add(2, 1) == 3
    assert call_count[0] == 2
    assert add(1, 2) == 3
    assert call_count[0] == 2


def test_ttl_cache_kwargs():
    call_count = [0]

    @ttl_cache(seconds=60)
    def compute(a, b=10):
        call_count[0] += 1
        return a * b

    assert compute(5, b=2) == 10
    assert call_count[0] == 1
    assert compute(5, b=2) == 10
    assert call_count[0] == 1
    assert compute(5, b=3) == 15
    assert call_count[0] == 2


def test_ttl_cache_expiry():
    call_count = [0]

    @ttl_cache(seconds=1)
    def compute(n):
        call_count[0] += 1
        return n * n

    assert compute(5) == 25
    assert call_count[0] == 1
    assert compute(5) == 25
    assert call_count[0] == 1
    time.sleep(1.1)
    assert compute(5) == 25
    assert call_count[0] == 2


def test_ttl_cache_lru_eviction():
    call_count = [0]

    @ttl_cache(seconds=60, maxsize=2)
    def compute(n):
        call_count[0] += 1
        return n * n

    compute(1)
    compute(2)
    assert call_count[0] == 2
    compute(1)
    assert call_count[0] == 2
    compute(3)
    assert call_count[0] == 3
    compute(2)
    assert call_count[0] == 4


def test_ttl_cache_clear():
    call_count = [0]

    @ttl_cache(seconds=60)
    def compute(n):
        call_count[0] += 1
        return n * n

    compute(5)
    assert call_count[0] == 1
    compute.cache_clear()
    compute(5)
    assert call_count[0] == 2


def test_ttl_cache_info():
    @ttl_cache(seconds=30, maxsize=64)
    def compute(n):
        return n * n

    info = compute.cache_info()
    assert info["size"] == 0
    assert info["maxsize"] == 64
    assert info["ttl"] == 30

    compute(5)
    info = compute.cache_info()
    assert info["size"] == 1


def test_ttl_cache_multiple_args():
    call_count = [0]

    @ttl_cache(seconds=60)
    def compute(a, b, c=0):
        call_count[0] += 1
        return a + b + c

    assert compute(1, 2, c=3) == 6
    assert call_count[0] == 1
    assert compute(1, 2, c=3) == 6
    assert call_count[0] == 1
    assert compute(1, 2, c=4) == 7
    assert call_count[0] == 2
