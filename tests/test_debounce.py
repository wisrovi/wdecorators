"""Tests for debounce decorator."""

import time

from wdecorators import debounce


def test_debounce_calls_after_wait():
    results = []

    @debounce(wait=0.05)
    def record(val):
        results.append(val)

    record(1)
    assert len(results) == 0
    time.sleep(0.1)
    assert len(results) == 1
    assert results[0] == 1


def test_debounce_multiple_rapid_calls():
    results = []

    @debounce(wait=0.1)
    def record(val):
        results.append(val)

    record(1)
    record(2)
    record(3)
    assert len(results) == 0
    time.sleep(0.2)
    assert len(results) == 1
    assert results[0] == 3


def test_debounce_immediate_first_call():
    results = []

    @debounce(wait=0.1, immediate=True)
    def record(val):
        results.append(val)

    record(1)
    assert len(results) == 1
    assert results[0] == 1


def test_debounce_immediate_subsequent_debounced():
    results = []

    @debounce(wait=0.05, immediate=True)
    def record(val):
        results.append(val)

    record(1)
    assert len(results) == 1
    record(2)
    assert len(results) == 1
    time.sleep(0.1)
    assert len(results) == 2
    assert results[1] == 2


def test_debounce_immediate_multiple_rapid():
    results = []

    @debounce(wait=0.05, immediate=True)
    def record(val):
        results.append(val)

    record(1)
    record(2)
    record(3)
    assert len(results) == 1
    time.sleep(0.1)
    assert len(results) == 2
    assert results[1] == 3


def test_debounce_returns_none():
    @debounce(wait=0.01)
    def my_func():
        return 42

    result = my_func()
    assert result is None


def test_debounce_timer_reset_on_new_call():
    results = []

    @debounce(wait=0.15)
    def record(val):
        results.append(val)

    record(1)
    time.sleep(0.1)
    record(2)
    time.sleep(0.1)
    assert len(results) == 0
    time.sleep(0.1)
    assert len(results) == 1
    assert results[0] == 2


def test_debounce_no_extra_calls_after_single():
    results = []

    @debounce(wait=0.02)
    def record(val):
        results.append(val)

    record(1)
    time.sleep(0.05)
    assert len(results) == 1
    time.sleep(0.1)
    assert len(results) == 1
