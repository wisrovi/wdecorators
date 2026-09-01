"""Example: mask_sensitive decorator - mask sensitive data."""

import logging

from wdecorators import mask_sensitive

logging.basicConfig(level=logging.DEBUG)


@mask_sensitive("password", "token", show_last=2)
def login(username, password, token):
    return f"User {username} logged in"


print(login("alice", "secret123", "xyz789"))
