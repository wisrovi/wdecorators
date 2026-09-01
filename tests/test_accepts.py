"""Tests for accepts decorator."""

import pytest

from wdecorators import accepts


def test_accepts_valid():
    @accepts(int, int)
    def add(a, b):
        return a + b

    assert add(3, 4) == 7


def test_accepts_invalid():
    @accepts(int, int)
    def add(a, b):
        return a + b

    with pytest.raises(TypeError):
        add("3", 4)


def test_accepts_multiple_types():
    @accepts(str, int, bool)
    def process(name, age, active):
        return f"{name}, {age}, {active}"

    result = process("Alice", 30, True)
    assert "Alice" in result
