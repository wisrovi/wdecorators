"""Example: trace_execution decorator - log function entry/exit."""

from wdecorators import trace_execution


@trace_execution
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@trace_execution
def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"


print(multiply(3, 4))
print(greet("Alice"))
