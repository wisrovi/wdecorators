"""Example: timeout decorator - enforce maximum execution time."""

import time

from wdecorators import TimeoutException, timeout


@timeout(seconds=2)
def long_task() -> str:
    """Simulate a long-running task that exceeds the timeout."""
    time.sleep(5)
    return "Finished"


try:
    print(long_task())
except TimeoutException as e:
    print(f"Timeout occurred: {e}")
