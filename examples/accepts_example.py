"""Example: accepts decorator - validate positional argument types."""

from wdecorators import accepts


@accepts(int, int)
def add(a, b):
    return a + b


print(add(3, 4))  # 7

try:
    add("3", 4)
except TypeError as e:
    print(f"TypeError: {e}")
