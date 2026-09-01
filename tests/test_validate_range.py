"""Tests for validate_range decorator."""

import pytest

from wdecorators import validate_range


def test_validate_range_valid():
    @validate_range("value", minimum=0, maximum=100)
    def set_percentage(value):
        return value

    assert set_percentage(value=50) == 50


def test_validate_range_below_minimum():
    @validate_range("value", minimum=0)
    def set_value(value):
        return value

    with pytest.raises(ValueError, match="is less than minimum 0"):
        set_value(value=-1)


def test_validate_range_above_maximum():
    @validate_range("value", maximum=100)
    def set_value(value):
        return value

    with pytest.raises(ValueError, match="is greater than maximum 100"):
        set_value(value=101)


def test_validate_range_min_only():
    @validate_range("value", minimum=10)
    def set_value(value):
        return value

    assert set_value(value=10) == 10
    assert set_value(value=20) == 20
    with pytest.raises(ValueError):
        set_value(value=9)


def test_validate_range_max_only():
    @validate_range("value", maximum=50)
    def set_value(value):
        return value

    assert set_value(value=50) == 50
    assert set_value(value=30) == 30
    with pytest.raises(ValueError):
        set_value(value=51)


def test_validate_range_no_bounds():
    @validate_range("value")
    def set_value(value):
        return value

    assert set_value(value=42) == 42


def test_validate_range_arg_not_found():
    @validate_range("missing_arg")
    def set_value(value):
        return value

    with pytest.raises(ValueError, match="Argument 'missing_arg' not found"):
        set_value(value=1)


def test_validate_range_non_numeric():
    @validate_range("value", minimum=0)
    def set_value(value):
        return value

    with pytest.raises(TypeError, match="Argument 'value' must be numeric"):
        set_value(value="not_a_number")


def test_validate_range_float_value():
    @validate_range("value", minimum=0.0, maximum=1.0)
    def set_value(value):
        return value

    assert set_value(value=0.5) == 0.5
    with pytest.raises(ValueError):
        set_value(value=1.5)


def test_validate_range_positional_arg():
    @validate_range("value", minimum=0, maximum=100)
    def set_value(value):
        return value

    assert set_value(50) == 50


def test_validate_range_with_default():
    @validate_range("value", minimum=0, maximum=100)
    def set_value(value=50):
        return value

    assert set_value() == 50
    with pytest.raises(ValueError):
        set_value(value=200)


def test_validate_range_boundary_values():
    @validate_range("value", minimum=0, maximum=100)
    def set_value(value):
        return value

    assert set_value(value=0) == 0
    assert set_value(value=100) == 100


@pytest.mark.asyncio
async def test_validate_range_async():
    @validate_range("value", minimum=0, maximum=100)
    async def set_value(value):
        return value

    result = await set_value(value=50)
    assert result == 50


@pytest.mark.asyncio
async def test_validate_range_async_violation():
    @validate_range("value", maximum=10)
    async def set_value(value):
        return value

    with pytest.raises(ValueError, match="is greater than maximum 10"):
        await set_value(value=20)
