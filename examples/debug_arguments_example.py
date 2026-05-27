"""Example: debug_arguments decorator - inspect function arguments."""

from wdecorators import debug_arguments


@debug_arguments
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@debug_arguments
def greet(name: str = "World") -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"


print(add(5, 10))
print(greet(name="Carlos"))
