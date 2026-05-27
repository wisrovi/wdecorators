"""Pytest configuration and shared fixtures."""

import logging
import pytest


@pytest.fixture(autouse=True)
def disable_logging():
    """Disable logging during tests to avoid cluttering output."""
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def sample_function():
    """Return a simple function for testing decorators."""

    def add(a, b):
        return a + b

    return add


@pytest.fixture
def async_sample_function():
    """Return a simple async function for testing async decorators."""

    async def async_add(a, b):
        return a + b

    return async_add
