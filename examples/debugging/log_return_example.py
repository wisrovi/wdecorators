"""Example: log_return decorator - print function return values."""

from wdecorators import log_return


@log_return
def square(n: int) -> int:
    """Return the square of a number."""
    return n * n


@log_return
def hello() -> str:
    """Return a greeting."""
    return "Hello world"


print(square(4))
print(hello())
