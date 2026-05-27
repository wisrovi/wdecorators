"""Tests for periodic_execution decorator."""

import time
import pytest
from wdecorators import periodic_execution


def test_periodic_execution_runs():
    calls = []

    @periodic_execution(interval=0.01)
    def worker():
        calls.append(1)

    thread = worker()
    time.sleep(0.05)
    thread.stop_event.set()
    thread.join(timeout=1)

    assert len(calls) >= 1


def test_periodic_execution_stop():
    calls = []

    @periodic_execution(interval=0.01)
    def worker():
        calls.append(1)

    thread = worker()
    thread.stop_event.set()
    thread.join(timeout=1)

    count_after_stop = len(calls)
    time.sleep(0.03)
    assert len(calls) == count_after_stop


def test_periodic_execution_with_args():
    results = []

    @periodic_execution(interval=0.01)
    def worker(msg):
        results.append(msg)

    thread = worker("hello")
    time.sleep(0.05)
    thread.stop_event.set()
    thread.join(timeout=1)

    assert len(results) >= 1
    assert all(r == "hello" for r in results)


def test_periodic_execution_interval_respected():
    timestamps = []

    @periodic_execution(interval=0.05)
    def worker():
        timestamps.append(time.time())

    thread = worker()
    time.sleep(0.12)
    thread.stop_event.set()
    thread.join(timeout=1)

    assert len(timestamps) >= 2
    for i in range(1, len(timestamps)):
        elapsed = timestamps[i] - timestamps[i - 1]
        assert elapsed >= 0.04


def test_periodic_execution_zero_interval():
    calls = []

    @periodic_execution(interval=0.0)
    def worker():
        calls.append(1)

    thread = worker()
    time.sleep(0.02)
    thread.stop_event.set()
    thread.join(timeout=1)

    assert len(calls) >= 1
