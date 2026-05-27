"""Tests for default_values decorator."""

from wdecorators import default_values


def test_default_values_applied():
    @default_values(timeout=30, retries=3)
    def connect(timeout, retries):
        return {"timeout": timeout, "retries": retries}

    result = connect()
    assert result["timeout"] == 30
    assert result["retries"] == 3


def test_default_values_overridden():
    @default_values(timeout=30)
    def connect(timeout):
        return timeout

    assert connect(timeout=60) == 60
