"""Example: count_calls decorator - track how many times a function is called."""

from wdecorators import count_calls


@count_calls
def say_hello(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}!"


print(say_hello("Alice"))
print(say_hello("Bob"))
print(f"Total calls: {say_hello.call_count}")
