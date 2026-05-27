"""Tests for time_execution decorator."""

import logging

import pytest
from wdecorators import time_execution


def test_time_execution_sync(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @time_execution
    def fast():
        return 42

    result = fast()
    assert result == 42
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    msg = record.getMessage()
    assert "fast" in msg
    assert "took" in msg
    assert "s" in msg


def test_time_execution_sync_with_args(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @time_execution
    def add(a, b):
        return a + b

    result = add(3, 7)
    assert result == 10
    msg = caplog.records[0].getMessage()
    assert "add" in msg
    assert "took" in msg


@pytest.mark.asyncio
async def test_time_execution_async(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @time_execution
    async def async_fast():
        return 99

    result = await async_fast()
    assert result == 99
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    msg = record.getMessage()
    assert "async_fast" in msg
    assert "took" in msg


@pytest.mark.asyncio
async def test_time_execution_async_with_args(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @time_execution
    async def async_add(a, b):
        return a + b

    result = await async_add(10, 20)
    assert result == 30
    msg = caplog.records[0].getMessage()
    assert "async_add" in msg
    assert "took" in msg


def test_time_execution_sync_elapsed_logged(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @time_execution
    def short_sleep():
        import time

        time.sleep(0.01)
        return "done"

    result = short_sleep()
    assert result == "done"
    msg = caplog.records[0].getMessage()
    assert "short_sleep" in msg
    assert float(msg.split("took ")[1].rstrip("s")) > 0


@pytest.mark.asyncio
async def test_time_execution_async_elapsed_logged(caplog):
    caplog.set_level(logging.INFO, logger="wdecorators")

    @time_execution
    async def async_short_sleep():
        import asyncio

        await asyncio.sleep(0.01)
        return "done"

    result = await async_short_sleep()
    assert result == "done"
    msg = caplog.records[0].getMessage()
    assert "async_short_sleep" in msg
    assert float(msg.split("took ")[1].rstrip("s")) > 0


def test_time_execution_sync_wrapper_metadata():
    @time_execution
    def my_sync():
        """Sync doc."""

    assert my_sync.__name__ == "my_sync"
    assert my_sync.__doc__ == "Sync doc."
    assert my_sync.__wrapped__ is not None


@pytest.mark.asyncio
async def test_time_execution_async_wrapper_metadata():
    @time_execution
    async def my_async():
        """Async doc."""

    assert my_async.__name__ == "my_async"
    assert my_async.__doc__ == "Async doc."
    assert my_async.__wrapped__ is not None
