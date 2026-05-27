"""Tests for require_authentication decorator."""

import pytest
from wdecorators import require_authentication


def test_require_authentication_passes():
    user = {"authenticated": True}

    @require_authentication(user)
    def secret():
        return "top secret"

    assert secret() == "top secret"


def test_require_authentication_fails():
    user = {"authenticated": False}

    @require_authentication(user)
    def secret():
        return "top secret"

    with pytest.raises(PermissionError):
        secret()


def test_require_authentication_no_key():
    user = {}

    @require_authentication(user)
    def secret():
        return "top secret"

    with pytest.raises(PermissionError):
        secret()
