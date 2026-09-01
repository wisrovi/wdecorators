"""Example: silent_fail decorator - silence exceptions and return None."""

from wdecorators import silent_fail


@silent_fail
def risky_operation() -> float:
    """An operation that raises an exception."""
    return 1 / 0


@silent_fail
def safe_operation() -> str:
    """A safe operation."""
    return "All good"


print(risky_operation())  # None (exception silenced)
print(safe_operation())  # "All good"
