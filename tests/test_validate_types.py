"""Tests for validate_types decorator."""

import pytest

from wdecorators import validate_types


def test_validate_types_valid():
    @validate_types(name=str, age=int)
    def info(name, age):
        return f"{name} is {age}"

    assert info(name="Alice", age=30) == "Alice is 30"


def test_validate_types_invalid():
    @validate_types(name=str, age=int)
    def info(name, age):
        return f"{name} is {age}"

    with pytest.raises(TypeError):
        info(name="Alice", age="thirty")


def test_validate_types_no_matching_kwargs():
    @validate_types(name=str)
    def info(name, age):
        return f"{name} is {age}"

    result = info(name="Alice", age=30)
    assert result == "Alice is 30"


def test_validate_types_valid_multiple_kwargs():
    @validate_types(name=str, age=int)
    def info(name, age):
        return f"{name} is {age}"

    result = info(age=30, name="Alice")
    assert result == "Alice is 30"


def test_validate_types_positional_args_not_validated():
    @validate_types(name=str)
    def info(name, age):
        return f"{name} is {age}"

    result = info("Alice", 30)
    assert result == "Alice is 30"
