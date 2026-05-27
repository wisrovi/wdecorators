"""Tests for log_return decorator."""

import logging

from wdecorators import log_return


def test_log_return_logs_result(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @log_return
    def square(n):
        return n * n

    result = square(5)
    assert result == 25
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    assert "square" in record.getMessage()
    assert "25" in record.getMessage()


def test_log_return_string_result(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @log_return
    def greet(name):
        return f"Hello, {name}!"

    result = greet("World")
    assert result == "Hello, World!"
    msg = caplog.records[0].getMessage()
    assert "greet" in msg
    assert "Hello, World!" in msg


def test_log_return_none_result(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @log_return
    def do_nothing():
        return None

    result = do_nothing()
    assert result is None
    msg = caplog.records[0].getMessage()
    assert "do_nothing" in msg
    assert "None" in msg


def test_log_return_complex_result(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @log_return
    def make_list():
        return [1, 2, 3]

    result = make_list()
    assert result == [1, 2, 3]
    msg = caplog.records[0].getMessage()
    assert "make_list" in msg
    assert "[1, 2, 3]" in msg


def test_log_return_preserves_multiple_calls(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @log_return
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    assert add(10, 20) == 30
    assert len(caplog.records) == 2


def test_log_return_wrapper_metadata():
    @log_return
    def my_func():
        """Docstring."""

    assert my_func.__name__ == "my_func"
    assert my_func.__wrapped__ is not None
