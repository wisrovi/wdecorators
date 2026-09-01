"""Tests for coerce_types decorator."""

import pytest

from wdecorators import coerce_types


def test_coerce_types_single_kwarg():
    @coerce_types(age=int)
    def process(age):
        return age

    assert process(age="30") == 30


def test_coerce_types_multiple_kwargs():
    @coerce_types(age=int, active=bool)
    def process(age, active):
        return (age, active)

    result = process(age="25", active="true")
    assert result == (25, True)


def test_coerce_types_uncoerced_args_passthrough():
    @coerce_types(age=int)
    def process(name, age):
        return (name, age)

    result = process(name="Alice", age="30")
    assert result == ("Alice", 30)


def test_coerce_types_missing_coercion_arg():
    @coerce_types(age=int, extra=str)
    def process(age, extra=None):
        return (age, extra)

    result = process(age="30")
    assert result == (30, None)


def test_coerce_types_invalid_coercion():
    @coerce_types(age=int)
    def process(age):
        return age

    with pytest.raises(TypeError, match="Cannot coerce argument 'age' to int"):
        process(age="not_a_number")


def test_coerce_types_float_to_int():
    @coerce_types(age=int)
    def process(age):
        return age

    assert process(age=10.7) == 10


def test_coerce_types_bool_from_string():
    @coerce_types(active=bool)
    def process(active):
        return active

    assert process(active="False") is True


@pytest.mark.asyncio
async def test_coerce_types_async():
    @coerce_types(age=int)
    async def process(age):
        return age

    result = await process(age="30")
    assert result == 30


@pytest.mark.asyncio
async def test_coerce_types_async_invalid():
    @coerce_types(age=int)
    async def process(age):
        return age

    with pytest.raises(TypeError, match="Cannot coerce argument 'age' to int"):
        await process(age="not_a_number")
