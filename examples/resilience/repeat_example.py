"""Example: repeat decorator - repeat function calls."""

from wdecorators import repeat

call_count = 0


@repeat(times=3, delay=0.2)
def poll():
    global call_count
    call_count += 1
    return f"poll-{call_count}"


results = poll()
print(f"Results: {results}")
print(f"Total calls: {call_count}")
