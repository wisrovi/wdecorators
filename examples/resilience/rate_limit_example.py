"""Example: rate_limit decorator - limit calls per second."""

import time

from wdecorators import rate_limit


@rate_limit(calls_per_second=2)
def say_hello(name: str) -> str:
    """Return a greeting, rate-limited to 2 calls/second."""
    return f"Hello, {name}!"


start = time.time()
for i in range(5):
    print(say_hello(f"User {i}"))
elapsed = time.time() - start
print(f"5 calls took {elapsed:.2f}s (expected ~2s)")
