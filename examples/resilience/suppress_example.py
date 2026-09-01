"""Example: suppress decorator - suppress specific exceptions."""

import asyncio

from wdecorators import suppress


@suppress(ValueError, ZeroDivisionError, fallback=0)
def divide(a, b):
    return a / b


print(divide(10, 2))  # 5.0
print(divide(10, 0))  # 0 (suppressed ZeroDivisionError)
print(divide(10, "a"))  # TypeError not suppressed


# Async example
@suppress(ValueError, fallback="default")
async def async_fetch():
    raise ValueError("API error")
    return "data"


result = asyncio.run(async_fetch())
print(f"Async result: {result}")
