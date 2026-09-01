"""Tests for validate_length decorator."""

import pytest

from wdecorators import validate_length


def test_validate_length_valid():
    @validate_length("name", minimum=1, maximum=10)
    def set_name(name):
        return name

    assert set_name(name="hello") == "hello"


def test_validate_length_minimum_violation():
    @validate_length("name", minimum=2)
    def set_name(name):
        return name

    with pytest.raises(ValueError, match="length 1 is less than minimum 2"):
        set_name(name="a")


def test_validate_length_maximum_violation():
    @validate_length("name", maximum=5)
    def set_name(name):
        return name

    with pytest.raises(ValueError, match="length 6 exceeds maximum 5"):
        set_name(name="abcdef")


def test_validate_length_min_only():
    @validate_length("name", minimum=3)
    def set_name(name):
        return name

    assert set_name(name="abc") == "abc"
    with pytest.raises(ValueError):
        set_name(name="ab")


def test_validate_length_max_only():
    @validate_length("name", maximum=3)
    def set_name(name):
        return name

    assert set_name(name="abc") == "abc"
    with pytest.raises(ValueError):
        set_name(name="abcd")


def test_validate_length_no_bounds():
    @validate_length("name")
    def set_name(name):
        return name

    assert set_name(name="any") == "any"


def test_validate_length_arg_not_found():
    @validate_length("missing_arg")
    def set_name(name):
        return name

    with pytest.raises(ValueError, match="Argument 'missing_arg' not found"):
        set_name(name="hello")


def test_validate_length_no_length():
    @validate_length("value", minimum=1)
    def process(value):
        return value

    with pytest.raises(TypeError, match="Argument 'value' must have length"):
        process(value=42)


def test_validate_length_positional_arg():
    @validate_length("name", minimum=1)
    def set_name(name):
        return name

    assert set_name("hello") == "hello"


def test_validate_length_with_default():
    @validate_length("name", minimum=1, maximum=10)
    def set_name(name="default"):
        return name

    assert set_name() == "default"
    with pytest.raises(ValueError):
        set_name(name="a" * 11)


def test_validate_length_list_arg():
    @validate_length("items", minimum=1, maximum=3)
    def process(items):
        return items

    assert process(items=[1, 2]) == [1, 2]
    with pytest.raises(ValueError):
        process(items=[])


@pytest.mark.asyncio
async def test_validate_length_async():
    @validate_length("name", minimum=1, maximum=10)
    async def set_name(name):
        return name

    result = await set_name(name="hello")
    assert result == "hello"


@pytest.mark.asyncio
async def test_validate_length_async_violation():
    @validate_length("name", minimum=2)
    async def set_name(name):
        return name

    with pytest.raises(ValueError, match="length 1 is less than minimum 2"):
        await set_name(name="a")
