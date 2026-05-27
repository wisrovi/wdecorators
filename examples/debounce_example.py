"""Example: debounce decorator - debounce function calls."""

import time
from wdecorators import debounce


call_log = []


@debounce(wait=0.5, immediate=True)
def on_input(value):
    call_log.append(value)
    print(f"Processed: {value}")


# Immediate first call
on_input("A")
on_input("B")
on_input("C")

time.sleep(0.7)
print(f"Calls processed: {call_log}")
