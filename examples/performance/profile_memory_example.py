"""Example: profile_memory decorator - trace memory usage."""

from wdecorators import profile_memory


@profile_memory
def create_large_list() -> list:
    """Create a large list to demonstrate memory profiling."""
    return [i for i in range(100000)]


@profile_memory
def create_small_list() -> list:
    """Create a small list."""
    return [1, 2, 3]


print(len(create_large_list()))
print(create_small_list())
