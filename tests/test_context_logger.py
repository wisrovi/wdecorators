"""Tests for context_logger decorator."""

import logging
import pytest
from wdecorators import context_logger


def test_context_logger_entry_exit(caplog):
    caplog.set_level(logging.INFO)

    @context_logger()
    def greet(name):
        return f"Hello {name}"

    result = greet("World")
    assert result == "Hello World"

    assert any("Entering greet" in r.message for r in caplog.records)
    assert any("Exiting greet" in r.message for r in caplog.records)


def test_context_logger_custom_name(caplog):
    caplog.set_level(logging.INFO)

    @context_logger(name="myapp.custom")
    def add(a, b):
        return a + b

    add(1, 2)

    records = [r for r in caplog.records if r.name == "myapp.custom"]
    assert len(records) == 2


def test_context_logger_exception(caplog):
    caplog.set_level(logging.ERROR)

    @context_logger()
    def crash():
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        crash()

    assert any("Error in crash" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_context_logger_async(caplog):
    caplog.set_level(logging.INFO)

    @context_logger(name="async_test")
    async def fetch_data():
        return "data"

    result = await fetch_data()
    assert result == "data"

    records = [r for r in caplog.records if r.name == "async_test"]
    assert len(records) == 2
    assert any("Entering fetch_data" in r.message for r in records)
