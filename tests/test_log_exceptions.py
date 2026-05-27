"""Tests for log_exceptions decorator."""

import asyncio
import pytest
from wdecorators.general import log_exceptions


def test_log_exceptions_sync_no_exception():
    @log_exceptions(fallback="fallback")
    def ok():
        return "success"

    assert ok() == "success"


def test_log_exceptions_sync_with_exception():
    @log_exceptions(fallback="fallback")
    def fail():
        raise ValueError("error")

    assert fail() == "fallback"


def test_log_exceptions_sync_no_fallback_with_exception():
    @log_exceptions(fallback=None)
    def fail():
        raise ValueError("error")

    assert fail() is None


def test_log_exceptions_sync_no_parentheses():
    @log_exceptions
    def ok():
        return "success"

    assert ok() == "success"


def test_log_exceptions_sync_no_parentheses_with_exception():
    @log_exceptions
    def fail():
        raise ValueError("error")

    assert fail() is None


def test_log_exceptions_async_no_exception():
    @log_exceptions(fallback="fallback")
    async def ok():
        return "success"

    assert asyncio.run(ok()) == "success"


def test_log_exceptions_async_with_exception():
    @log_exceptions(fallback="fallback")
    async def fail():
        raise ValueError("error")

    assert asyncio.run(fail()) == "fallback"


def test_log_exceptions_async_no_fallback_with_exception():
    @log_exceptions(fallback=None)
    async def fail():
        raise ValueError("error")

    assert asyncio.run(fail()) is None
