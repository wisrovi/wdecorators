"""Tests for to_json decorator."""

import json

import pytest

from wdecorators import to_json


def test_to_json_dict():
    @to_json
    def get_data():
        return {"name": "Alice", "age": 30}

    result = get_data()
    assert json.loads(result) == {"name": "Alice", "age": 30}


def test_to_json_list():
    @to_json
    def get_items():
        return [1, 2, 3]

    result = get_items()
    assert json.loads(result) == [1, 2, 3]


def test_to_json_string():
    @to_json
    def get_string():
        return "hello"

    result = get_string()
    assert result == '"hello"' or json.loads(result) == "hello"


def test_to_json_int():
    @to_json
    def get_int():
        return 42

    result = get_int()
    assert json.loads(result) == 42


def test_to_json_nested():
    @to_json
    def get_nested():
        return {"a": [1, {"b": 2}]}

    result = get_nested()
    assert json.loads(result) == {"a": [1, {"b": 2}]}


def test_to_json_non_serializable():
    @to_json
    def get_object():
        return {"obj": object()}

    with pytest.raises(TypeError):
        get_object()


def test_to_json_custom_class():
    class Custom:
        pass

    @to_json
    def get_custom():
        return Custom()

    with pytest.raises(TypeError):
        get_custom()
