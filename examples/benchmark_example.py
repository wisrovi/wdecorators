"""Example: benchmark decorator - measure function execution time."""

import time

from wdecorators import benchmark


@benchmark
def slow_task():
    """Simulate a slow operation."""
    time.sleep(1)
    return "Completed"


@benchmark
def fast_task():
    """Simulate a fast operation."""
    return "Done"


print(slow_task())
print(fast_task())
