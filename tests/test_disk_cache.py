"""Tests for disk_cache decorator."""

import json
import os
import pickle
import tempfile
from wdecorators import disk_cache


def test_disk_cache_json():
    cache_file = tempfile.mktemp(suffix=".json")

    @disk_cache(filename=cache_file, serializer="json")
    def compute(n):
        return {"input": n, "result": n * n}

    result1 = compute(5)
    result2 = compute(5)
    assert result1 == result2
    assert result1["result"] == 25
    assert os.path.exists(cache_file)
    os.remove(cache_file)


def test_disk_cache_clear():
    cache_file = tempfile.mktemp(suffix=".pkl")

    @disk_cache(filename=cache_file, serializer="pickle")
    def compute(n):
        return n * n

    compute(5)
    assert os.path.exists(cache_file)
    compute.cache_clear()
    assert not os.path.exists(cache_file)


def test_disk_cache_pickle():
    cache_file = tempfile.mktemp(suffix=".pkl")

    @disk_cache(filename=cache_file, serializer="pickle")
    def compute(n):
        return {"input": n, "result": n * n}

    result1 = compute(5)
    result2 = compute(5)
    assert result1 == result2
    assert result1["result"] == 25
    os.remove(cache_file)


def test_disk_cache_hit_miss():
    cache_file = tempfile.mktemp(suffix=".json")

    @disk_cache(filename=cache_file, serializer="json")
    def compute(n):
        return n * 2

    assert compute(3) == 6
    assert compute(3) == 6
    assert compute(5) == 10
    os.remove(cache_file)


def test_disk_cache_invalid_serializer():
    try:
        @disk_cache(filename="test.pkl", serializer="invalid")
        def compute(n):
            return n
    except ValueError as e:
        assert "Unsupported serializer" in str(e)


def test_disk_cache_corrupted_json():
    cache_file = tempfile.mktemp(suffix=".json")
    with open(cache_file, "w") as f:
        f.write("corrupted data")

    call_count = [0]

    @disk_cache(filename=cache_file, serializer="json")
    def compute(n):
        call_count[0] += 1
        return n * n

    assert compute(5) == 25
    assert call_count[0] == 1
    os.remove(cache_file)


def test_disk_cache_corrupted_pickle():
    cache_file = tempfile.mktemp(suffix=".pkl")
    with open(cache_file, "wb") as f:
        f.write(b"corrupted data")

    call_count = [0]

    @disk_cache(filename=cache_file, serializer="pickle")
    def compute(n):
        call_count[0] += 1
        return n * n

    assert compute(5) == 25
    assert call_count[0] == 1
    os.remove(cache_file)


def test_disk_cache_empty_file():
    cache_file = tempfile.mktemp(suffix=".pkl")
    with open(cache_file, "wb") as f:
        pass

    call_count = [0]

    @disk_cache(filename=cache_file, serializer="pickle")
    def compute(n):
        call_count[0] += 1
        return n * n

    assert compute(5) == 25
    assert call_count[0] == 1
    os.remove(cache_file)


def test_disk_cache_no_file():
    cache_file = tempfile.mktemp(suffix=".json")
    if os.path.exists(cache_file):
        os.remove(cache_file)

    call_count = [0]

    @disk_cache(filename=cache_file, serializer="json")
    def compute(n):
        call_count[0] += 1
        return n * n

    assert compute(5) == 25
    assert call_count[0] == 1
    assert compute(5) == 25
    assert call_count[0] == 1
    os.remove(cache_file)


def test_disk_cache_kwargs():
    cache_file = tempfile.mktemp(suffix=".json")

    @disk_cache(filename=cache_file, serializer="json")
    def compute(a, b=10):
        return a + b

    assert compute(5, b=2) == 7
    assert compute(5, b=2) == 7
    assert compute(5, b=3) == 8
    os.remove(cache_file)


def test_disk_cache_persists_across_calls():
    cache_file = tempfile.mktemp(suffix=".pkl")

    @disk_cache(filename=cache_file, serializer="pickle")
    def compute(n):
        return n * n

    assert compute(4) == 16

    @disk_cache(filename=cache_file, serializer="pickle")
    def compute2(n):
        return n * n * 100

    assert compute2(4) == 16
    os.remove(cache_file)
