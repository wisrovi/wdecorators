"""Example: throttle decorator - throttle function calls."""

import time
from wdecorators import throttle

call_times = []


@throttle(interval=1.0)
def on_event(name):
    call_times.append(time.monotonic())
    print(f"Event: {name}")


# Rapid calls - only first and every 1s should pass
for i in range(5):
    on_event(f"click-{i}")
    time.sleep(0.1)

print(f"Calls executed: {len(call_times)} (expected ~1)")
