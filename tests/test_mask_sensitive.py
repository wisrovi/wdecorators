"""Tests for mask_sensitive decorator."""

from wdecorators import mask_sensitive


def test_mask_sensitive_full_mask():
    @mask_sensitive("password")
    def login(password, username):
        return f"{username}:{password}"

    assert login(password="secret123", username="alice") == "alice:secret123"


def test_mask_sensitive_partial_mask():
    @mask_sensitive("password", show_last=2)
    def login(password, username):
        return f"{username}:{password}"

    result = login(password="secret123", username="alice")
    assert result == "alice:secret123"


def test_mask_sensitive_no_match():
    @mask_sensitive("token")
    def login(password, username):
        return f"{username}:{password}"

    result = login(password="secret123", username="alice")
    assert result == "alice:secret123"


def test_mask_sensitive_non_string():
    @mask_sensitive("count")
    def show(count):
        return count

    result = show(count=42)
    assert result == 42


def test_mask_sensitive_empty_string():
    @mask_sensitive("password", show_last=2)
    def login(password, username):
        return f"{username}:{password}"

    result = login(password="", username="alice")
    assert result == "alice:"
