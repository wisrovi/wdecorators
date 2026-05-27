"""Tests for profile_memory decorator."""

import logging

import pytest
from wdecorators import profile_memory


def test_profile_memory_logs_memory(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @profile_memory
    def make_small_list():
        return [1, 2, 3]

    result = make_small_list()
    assert result == [1, 2, 3]
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    msg = record.getMessage()
    assert "Memory in make_small_list" in msg
    assert "KB" in msg


def test_profile_memory_larger_allocation(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @profile_memory
    def make_big_list():
        return list(range(10000))

    result = make_big_list()
    assert len(result) == 10000
    assert len(caplog.records) == 1
    msg = caplog.records[0].getMessage()
    assert "Memory in make_big_list" in msg


def test_profile_memory_no_return_value(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @profile_memory
    def side_effect_func():
        a = [i for i in range(100)]

    result = side_effect_func()
    assert result is None
    assert len(caplog.records) == 1


def test_profile_memory_with_args(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @profile_memory
    def create_nested(n):
        return [[i] for i in range(n)]

    result = create_nested(500)
    assert len(result) == 500
    msg = caplog.records[0].getMessage()
    assert "Memory in create_nested" in msg


def test_profile_memory_wrapper_metadata():
    @profile_memory
    def my_func():
        """Profile me."""
        return 0

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "Profile me."
    assert my_func.__wrapped__ is not None
