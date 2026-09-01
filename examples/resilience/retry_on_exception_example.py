"""Example: retry_on_exception decorator - retry on specific exceptions."""

from wdecorators import retry_on_exception


@retry_on_exception(retries=3, delay=1, exceptions=(ZeroDivisionError,))
def risky_divide(x: float) -> float:
    """Divide 10 by x, retrying on ZeroDivisionError."""
    return 10 / x


# This will retry 3 times then raise RuntimeError
try:
    risky_divide(0)
except RuntimeError as e:
    print(f"Failed after retries: {e}")
