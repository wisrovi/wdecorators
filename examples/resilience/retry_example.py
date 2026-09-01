"""Example: retry decorator - retry a function on failure."""

import random

from wdecorators import retry


@retry(times=5)
def may_fail() -> str:
    """Succeed with 50% probability, retry on failure."""
    if random.random() < 0.5:
        raise ValueError("Random failure occurred")
    return "Success!"


result = may_fail()
print(f"Result: {result}")
