"""Tests for conditional decorator."""

import asyncio

from wdecorators import conditional


def test_conditional_true():
    @conditional(lambda: True)
    def run():
        return "executed"

    assert run() == "executed"


def test_conditional_false():
    @conditional(lambda: False)
    def skip():
        return "should not run"

    assert skip() is None


def test_conditional_true_async():
    @conditional(lambda: True)
    async def run():
        return "executed"

    assert asyncio.run(run()) == "executed"


def test_conditional_false_async():
    @conditional(lambda: False)
    async def skip():
        return "should not run"

    assert asyncio.run(skip()) is None
