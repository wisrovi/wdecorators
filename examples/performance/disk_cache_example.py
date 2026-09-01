"""Example: disk_cache decorator - cache results to disk."""

import os

from wdecorators import disk_cache


@disk_cache("square_cache.pkl")
def square(n: int) -> int:
    """Compute the square of a number (expensive simulation)."""
    print(f"Computing square of {n}...")
    return n * n


print(square(5))  # Computes
print(square(5))  # Reads from cache
print(square(7))  # Computes

# Cleanup
if os.path.exists("square_cache.pkl"):
    os.remove("square_cache.pkl")
