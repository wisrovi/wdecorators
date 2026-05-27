"""Tests for returns decorator."""

import pytest
from wdecorators import returns


def test_returns_matching_type():
    @returns(int)
    def get_id():
        return 42

    assert get_id() == 42


def test_returns_with_args():
    @returns(str)
    def greet(name):
        return f"Hello, {name}"

    assert greet("Alice") == "Hello, Alice"


def test_returns_mismatched_type():
    @returns(int)
    def get_id():
        return "not_an_int"

    with pytest.raises(TypeError, match="get_id expected return type int, got str"):
        get_id()


def test_returns_none_vs_type():
    @returns(str)
    def get_none():
        return None

    with pytest.raises(
        TypeError, match="get_none expected return type str, got NoneType"
    ):
        get_none()


def test_returns_subclass():
    class Animal:
        pass

    class Dog(Animal):
        pass

    @returns(Animal)
    def get_pet():
        return Dog()

    result = get_pet()
    assert isinstance(result, Dog)


def test_returns_float_expected_int():
    @returns(int)
    def get_float():
        return 3.14

    with pytest.raises(TypeError, match="expected return type int, got float"):
        get_float()
