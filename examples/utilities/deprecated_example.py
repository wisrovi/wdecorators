"""Example: deprecated decorator - warn about deprecated functions."""

import warnings

from wdecorators import deprecated


@deprecated(version="1.0.0", alternative="new_function")
def old_function():
    return "Result from old function"


warnings.simplefilter("always")
print(old_function())
