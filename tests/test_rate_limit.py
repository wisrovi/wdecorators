"""Tests for rate_limit decorator."""

import time

from wdecorators import rate_limit


def test_rate_limit_first_call_passes_immediately():
    call_count = [0]

    @rate_limit(calls_per_second=10)
    def my_func():
        call_count[0] += 1
        return "ok"

    start = time.perf_counter()
    result = my_func()
    elapsed = time.perf_counter() - start
    assert result == "ok"
    assert call_count[0] == 1
    assert elapsed < 0.05


def test_rate_limit_second_call_delayed():
    call_count = [0]

    @rate_limit(calls_per_second=10)
    def my_func():
        call_count[0] += 1
        return call_count[0]

    my_func()
    start = time.perf_counter()
    result = my_func()
    elapsed = time.perf_counter() - start
    assert result == 2
    assert call_count[0] == 2
    assert elapsed >= 0.09


def test_rate_limit_excess_calls_are_delayed():
    call_count = [0]

    @rate_limit(calls_per_second=5)
    def my_func():
        call_count[0] += 1
        return call_count[0]

    my_func()
    my_func()
    my_func()
    assert call_count[0] == 3


def test_rate_limit_slow_calls_not_delayed():
    call_count = [0]

    @rate_limit(calls_per_second=10)
    def my_func():
        call_count[0] += 1
        return call_count[0]

    my_func()
    time.sleep(0.15)
    start = time.perf_counter()
    my_func()
    elapsed = time.perf_counter() - start
    assert elapsed < 0.05
    assert call_count[0] == 2


def test_rate_limit_returns_function_result():
    @rate_limit(calls_per_second=100)
    def add(a, b):
        return a + b

    assert add(2, 3) == 5
    assert add(10, 20) == 30


def test_rate_limit_multiple_fast_calls():
    call_times = []

    @rate_limit(calls_per_second=10)
    def record():
        call_times.append(time.perf_counter())

    for _ in range(5):
        record()

    assert len(call_times) == 5
    for i in range(1, len(call_times)):
        gap = call_times[i] - call_times[i - 1]
        assert gap >= 0.09
