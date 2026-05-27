"""Example: log_exceptions decorator - catch and log exceptions gracefully."""

from wdecorators.general import log_exceptions_general


@log_exceptions_general
def divide(a: float, b: float) -> float:
    """Divide two numbers, returning None on error."""
    return a / b


@log_exceptions_general(fallback=0)
def risky_operation() -> int:
    """An operation that always fails."""
    raise ValueError("Something went wrong!")
    return 42


print(divide(10, 2))  # 5.0
print(divide(10, 0))  # None (logs error)
print(risky_operation())  # 0 (fallback)
