"""Tests for throttle decorator."""

import time

from wdecorators import throttle


def test_throttle_first_call_passes():
    call_count = [0]

    @throttle(interval=1)
    def my_func():
        call_count[0] += 1
        return "ok"

    result = my_func()
    assert result == "ok"
    assert call_count[0] == 1


def test_throttle_subsequent_call_within_interval_dropped():
    call_count = [0]

    @throttle(interval=0.5)
    def my_func():
        call_count[0] += 1
        return "ok"

    assert my_func() == "ok"
    assert my_func() is None
    assert call_count[0] == 1


def test_throttle_call_after_interval_passes():
    call_count = [0]

    @throttle(interval=0.05)
    def my_func():
        call_count[0] += 1
        return "ok"

    assert my_func() == "ok"
    assert my_func() is None
    assert call_count[0] == 1
    time.sleep(0.1)
    assert my_func() == "ok"
    assert call_count[0] == 2


def test_throttle_multiple_dropped_calls():
    call_count = [0]

    @throttle(interval=0.1)
    def my_func():
        call_count[0] += 1
        return "ok"

    assert my_func() == "ok"
    assert my_func() is None
    assert my_func() is None
    assert call_count[0] == 1
    time.sleep(0.15)
    assert my_func() == "ok"
    assert call_count[0] == 2


def test_throttle_interval_reset_on_allowed_call():
    call_count = [0]

    @throttle(interval=0.05)
    def my_func():
        call_count[0] += 1

    my_func()
    time.sleep(0.1)
    my_func()
    time.sleep(0.02)
    my_func()
    assert call_count[0] == 2
    time.sleep(0.1)
    my_func()
    assert call_count[0] == 3


def test_throttle_sequential_after_interval():
    call_count = [0]

    @throttle(interval=0.03)
    def my_func():
        call_count[0] += 1
        return call_count[0]

    assert my_func() == 1
    assert my_func() is None
    time.sleep(0.05)
    assert my_func() == 2
    assert my_func() is None
    time.sleep(0.05)
    assert my_func() == 3
