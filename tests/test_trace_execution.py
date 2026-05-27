"""Tests for trace_execution decorator."""

import logging

from wdecorators import trace_execution


def test_trace_execution_logs_entry_and_exit(caplog):
    caplog.set_level(logging.DEBUG, logger="wdecorators")

    @trace_execution
    def multiply(a, b):
        return a * b

    result = multiply(3, 4)
    assert result == 12
    assert len(caplog.records) == 2

    assert caplog.records[0].levelname == "DEBUG"
    assert "Entering" in caplog.records[0].getMessage()
    assert "multiply" in caplog.records[0].getMessage()

    assert caplog.records[1].levelname == "DEBUG"
    assert "Exiting" in caplog.records[1].getMessage()
    assert "multiply" in caplog.records[1].getMessage()


def test_trace_execution_no_args(caplog):
    caplog.set_level(logging.DEBUG, logger="wdecorators")

    @trace_execution
    def constant():
        return 99

    result = constant()
    assert result == 99
    assert len(caplog.records) == 2


def test_trace_execution_with_kwargs(caplog):
    caplog.set_level(logging.DEBUG, logger="wdecorators")

    @trace_execution
    def greet(name, greeting="Hi"):
        return f"{greeting}, {name}!"

    result = greet("Alice", greeting="Hello")
    assert result == "Hello, Alice!"
    assert len(caplog.records) == 2


def test_trace_execution_multiple_calls(caplog):
    caplog.set_level(logging.DEBUG, logger="wdecorators")

    @trace_execution
    def add(a, b):
        return a + b

    add(1, 2)
    add(3, 4)
    assert len(caplog.records) == 4


def test_trace_execution_wrapper_metadata():
    @trace_execution
    def my_func():
        """My docstring."""
        return 42

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "My docstring."
    assert my_func.__wrapped__ is not None
