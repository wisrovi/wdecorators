"""Example: memoize decorator - cache function results in memory."""

import time

from wdecorators import memoize


@memoize
def slow_square(n: int) -> int:
    """Compute square with a simulated delay."""
    time.sleep(2)
    return n * n


print(slow_square(4))  # Takes 2 seconds
print(slow_square(4))  # Instant (cached)
print(slow_square(5))  # Takes 2 seconds
print(slow_square(5))  # Instant (cached)
