"""Example: synchronized decorator - thread-safe execution."""

import threading

from wdecorators import synchronized

counter = 0


@synchronized()
def increment():
    global counter
    current = counter
    # Simulate a race condition without the lock
    import time

    time.sleep(0.01)
    counter = current + 1


threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(f"Counter (expected 10): {counter}")
