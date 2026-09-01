"""Tests for ensure_kwargs decorator."""

import pytest

from wdecorators import ensure_kwargs


def test_positional_to_kwargs():
    @ensure_kwargs
    def connect(*, host, port):
        return f"{host}:{port}"

    result = connect("localhost", 8080)
    assert result == "localhost:8080"


def test_mixed_args():
    @ensure_kwargs
    def configure(*, host, port, timeout):
        return {"host": host, "port": port, "timeout": timeout}

    result = configure("example.com", 443, timeout=30)
    assert result == {"host": "example.com", "port": 443, "timeout": 30}


def test_all_kwargs():
    @ensure_kwargs
    def greet(*, greeting, name):
        return f"{greeting}, {name}"

    result = greet(greeting="Hi", name="Alice")
    assert result == "Hi, Alice"


def test_no_args():
    @ensure_kwargs
    def constant():
        return 42

    result = constant()
    assert result == 42


def test_positional_no_kwargs():
    @ensure_kwargs
    def add(*, a, b):
        return a + b

    result = add(3, 4)
    assert result == 7


@pytest.mark.asyncio
async def test_ensure_kwargs_async():
    @ensure_kwargs
    async def fetch(*, url, timeout):
        return {"url": url, "timeout": timeout}

    result = await fetch("https://example.com", 10)
    assert result == {"url": "https://example.com", "timeout": 10}
