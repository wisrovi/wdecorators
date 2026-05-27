"""Tests for ignore_kwargs decorator."""

from wdecorators import ignore_kwargs


def test_ignore_kwargs():
    @ignore_kwargs("unused", "deprecated_opt")
    def process(data):
        return data

    assert process("test", unused="ignored") == "test"


def test_ignore_kwargs_preserves_valid():
    @ignore_kwargs("unused")
    def process(data, flag=False):
        return {"data": data, "flag": flag}

    result = process("hello", flag=True, unused="ignored")
    assert result["flag"] is True
    assert result["data"] == "hello"
