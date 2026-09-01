"""Example: time_execution decorator - measure execution duration."""

import time

from wdecorators import time_execution


@time_execution
def slow_function() -> str:
    """Simulate a slow function."""
    time.sleep(1.5)
    return "Finished"


@time_execution
def fast_function() -> str:
    """Simulate a fast function."""
    return "Quick!"


print(slow_function())
print(fast_function())
