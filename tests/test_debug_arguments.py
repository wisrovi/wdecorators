"""Tests for debug_arguments decorator."""

import logging
from unittest.mock import ANY

import pytest

from wdecorators import debug_arguments


def test_debug_arguments_logs_args_and_kwargs(caplog):
    caplog.set_level(logging.DEBUG, logger="wdecorators")

    @debug_arguments
    def greet(greeting, name, punctuation="!"):
        return f"{greeting}, {name}{punctuation}"

    result = greet("Hello", "Alice", punctuation="?")
    assert result == "Hello, Alice?"
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "DEBUG"
    assert "greet" in record.getMessage()
    assert "Hello" in record.getMessage()
    assert "Alice" in record.getMessage()


def test_debug_arguments_no_args(caplog):
    caplog.set_level(logging.DEBUG, logger="wdecorators")

    @debug_arguments
    def forty_two():
        return 42

    result = forty_two()
    assert result == 42
    assert len(caplog.records) == 1
    assert "forty_two" in caplog.records[0].getMessage()


def test_debug_arguments_only_kwargs(caplog):
    caplog.set_level(logging.DEBUG, logger="wdecorators")

    @debug_arguments
    def build_point(x=0, y=0):
        return (x, y)

    result = build_point(x=3, y=4)
    assert result == (3, 4)
    assert len(caplog.records) == 1
    msg = caplog.records[0].getMessage()
    assert "build_point" in msg
    assert "x=3" in msg or "3" in msg
    assert "y=4" in msg or "4" in msg


def test_debug_arguments_preserves_return_value():
    @debug_arguments
    def multiply(a, b):
        return a * b

    assert multiply(3, 7) == 21
    assert multiply(-1, 5) == -5


def test_debug_arguments_wrapper_metadata():
    @debug_arguments
    def my_func(a, b):
        """Docstring."""
        return a + b

    assert my_func.__name__ == "my_func"
    assert my_func.__wrapped__ is not None
