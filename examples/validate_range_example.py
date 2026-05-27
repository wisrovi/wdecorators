"""Example: validate_range decorator - validate numeric range."""

from wdecorators import validate_range


@validate_range(arg="value", minimum=0, maximum=100)
def set_percentage(value):
    return f"Percentage set to {value}%"


print(set_percentage(50))  # OK

try:
    set_percentage(150)
except ValueError as e:
    print(f"ValueError: {e}")

try:
    set_percentage(-1)
except ValueError as e:
    print(f"ValueError: {e}")
