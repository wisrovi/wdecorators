"""Example: validate_types decorator - enforce runtime type checking."""

from wdecorators import validate_types


@validate_types(name=str, age=int)
def person_info(name: str, age: int) -> str:
    """Return formatted person info with type validation."""
    return f"{name} is {age} years old"


print(person_info(name="Carlos", age=30))  # Works

try:
    print(person_info(name="Carlos", age="thirty"))  # Fails
except TypeError as e:
    print(f"Type error: {e}")
