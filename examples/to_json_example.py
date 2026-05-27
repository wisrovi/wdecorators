"""Example: to_json decorator - convert return value to JSON string."""

from wdecorators import to_json


@to_json
def get_data() -> dict:
    """Return a dictionary that will be JSON-serialized."""
    return {"name": "Alice", "age": 25, "languages": ["Python", "Go"]}


result = get_data()
print(result)
print(type(result))  # <class 'str'>
