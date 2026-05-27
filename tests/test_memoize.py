"""Tests for memoize decorator."""

from wdecorators import memoize


def test_memoize_caches_result():
    call_count = [0]

    @memoize
    def compute(n):
        call_count[0] += 1
        return n * n

    assert compute(5) == 25
    assert call_count[0] == 1
    assert compute(5) == 25
    assert call_count[0] == 1  # Cached, no new call
    assert compute(7) == 49
    assert call_count[0] == 2


def test_memoize_different_args():
    @memoize
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    assert add(2, 1) == 3  # Different args, different cache key
    assert add(1, 2) == 3
