"""Tests for notify_on_error decorator."""

import pytest

from wdecorators import notify_on_error


def test_notify_on_error_called():
    notified = []

    def callback(error):
        notified.append(str(error))

    @notify_on_error(callback)
    def fail():
        raise ValueError("Something broke")

    with pytest.raises(ValueError):
        fail()

    assert len(notified) == 1
    assert "Something broke" in notified[0]


def test_notify_on_error_success():
    notified = []

    def callback(error):
        notified.append(error)

    @notify_on_error(callback)
    def ok():
        return "success"

    assert ok() == "success"
    assert len(notified) == 0


def test_notify_on_error_callback_receives_exception():
    received = []

    def callback(error):
        received.append(error)

    @notify_on_error(callback)
    def fail():
        raise RuntimeError("Custom error")

    with pytest.raises(RuntimeError):
        fail()

    assert len(received) == 1
    assert isinstance(received[0], RuntimeError)
    assert str(received[0]) == "Custom error"


@pytest.mark.asyncio
async def test_notify_on_error_async_called():
    notified = []

    def callback(error):
        notified.append(str(error))

    @notify_on_error(callback)
    async def fail():
        raise ValueError("Something broke")

    with pytest.raises(ValueError):
        await fail()

    assert len(notified) == 1
    assert "Something broke" in notified[0]


@pytest.mark.asyncio
async def test_notify_on_error_async_success():
    notified = []

    def callback(error):
        notified.append(error)

    @notify_on_error(callback)
    async def ok():
        return "success"

    result = await ok()
    assert result == "success"
    assert len(notified) == 0


@pytest.mark.asyncio
async def test_notify_on_error_async_callback_receives_exception():
    received = []

    def callback(error):
        received.append(error)

    @notify_on_error(callback)
    async def fail():
        raise RuntimeError("Custom error")

    with pytest.raises(RuntimeError):
        await fail()

    assert len(received) == 1
    assert isinstance(received[0], RuntimeError)
    assert str(received[0]) == "Custom error"
