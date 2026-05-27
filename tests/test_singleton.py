"""Tests for singleton decorator."""

from wdecorators import singleton


def test_singleton_returns_same_instance():
    @singleton
    class Database:
        def __init__(self):
            self.value = 42

    db1 = Database()
    db2 = Database()

    assert db1 is db2
    assert db1.value == 42


def test_singleton_preserves_attributes():
    @singleton
    class Config:
        def __init__(self):
            self.loaded = True

    cfg = Config()
    assert cfg.loaded is True
