"""Example: validate_length decorator - validate argument length."""

from wdecorators import validate_length


@validate_length(arg="name", minimum=2, maximum=50)
def set_name(name):
    return f"Name set to '{name}'"


print(set_name("Alice"))  # OK

try:
    set_name("A")
except ValueError as e:
    print(f"ValueError: {e}")

try:
    set_name("A" * 100)
except ValueError as e:
    print(f"ValueError: {e}")
