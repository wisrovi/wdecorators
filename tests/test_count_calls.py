"""Tests for count_calls decorator."""

from wdecorators import count_calls


def test_count_calls_tracks_call_count():
    @count_calls
    def foo():
        return "bar"

    assert foo.call_count == 0
    foo()
    assert foo.call_count == 1
    foo()
    foo()
    assert foo.call_count == 3


def test_count_calls_result():
    @count_calls
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
    assert add(10, 20) == 30
