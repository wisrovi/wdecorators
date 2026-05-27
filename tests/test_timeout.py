"""Tests for timeout decorator."""

import asyncio
import platform
import threading
import time
import pytest
from wdecorators import timeout, TimeoutException


def test_timeout_success():
    @timeout(seconds=5)
    def fast():
        return 42

    assert fast() == 42


def test_timeout_exception():
    @timeout(seconds=1)
    def slow():
        time.sleep(3)
        return "done"

    with pytest.raises(TimeoutException):
        slow()


def test_timeout_not_triggered():
    @timeout(seconds=5)
    def quick():
        time.sleep(0.01)
        return "done"

    assert quick() == "done"


@pytest.mark.asyncio
async def test_timeout_async():
    @timeout(seconds=1)
    async def fast():
        return 42

    result = await fast()
    assert result == 42


@pytest.mark.asyncio
async def test_timeout_async_exception():
    @timeout(seconds=1)
    async def slow():
        await asyncio.sleep(3)
        return "done"

    with pytest.raises(TimeoutException):
        await slow()


@pytest.mark.asyncio
async def test_timeout_async_not_triggered():
    @timeout(seconds=5)
    async def quick():
        await asyncio.sleep(0.01)
        return "done"

    result = await quick()
    assert result == "done"


def test_timeout_windows_success(mocker):
    mocker.patch.object(platform, "system", return_value="Windows")

    @timeout(seconds=5)
    def fast():
        return 42

    assert fast() == 42


def test_timeout_windows_exception(mocker):
    mocker.patch.object(platform, "system", return_value="Windows")

    @timeout(seconds=1)
    def slow():
        time.sleep(3)
        return "done"

    with pytest.raises(TimeoutException):
        slow()


def test_timeout_windows_not_triggered(mocker):
    mocker.patch.object(platform, "system", return_value="Windows")

    @timeout(seconds=5)
    def quick():
        time.sleep(0.01)
        return "done"

    assert quick() == "done"


def test_timeout_windows_propagates_exception(mocker):
    mocker.patch.object(platform, "system", return_value="Windows")

    @timeout(seconds=5)
    def fail():
        raise ValueError("boom")

    with pytest.raises(ValueError):
        fail()
