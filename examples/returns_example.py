"""Example: returns decorator - validate return type."""

from wdecorators import returns


@returns(int)
def get_id():
    return 42


@returns(str)
def get_name():
    return "Alice"


print(get_id())
print(get_name())

try:
    @returns(int)
    def broken():
        return "not a number"
    broken()
except TypeError as e:
    print(f"TypeError: {e}")
